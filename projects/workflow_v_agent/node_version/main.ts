import { generateText } from "ai";
import { google } from "@ai-sdk/google";
import * as dotenv from "dotenv";
import chalk from "chalk";

dotenv.config();

// Initialize the model
const model = google("gemini-2.0-flash");

// Add Node.js type definition
import { stdin, exit } from "process";

interface GenerateConfig {
  temperature: number;
  topP: number;
  topK: number;
  maxTokens: number;
}

const generateConfig: GenerateConfig = {
  temperature: 0.7,
  topP: 0.95,
  topK: 20,
  maxTokens: 100,
};

async function generateHaiku(
  prompt: string,
  feedback?: string,
  previousHaiku?: string
): Promise<string> {
  const messages = [
    {
      role: "user" as const,
      content: `Prompt: ${prompt}

Requirements:
1. Be exactly three lines
2. Follow 5-7-5 syllable pattern strictly
3. Use vivid imagery

Please write a haiku.`,
    },
  ];

  if (previousHaiku && feedback) {
    messages.push({
      role: "user" as const,
      content: `Your previous haiku was:
${previousHaiku}

The feedback was: ${feedback}

Please write a new haiku that addresses this feedback.`,
    });
  }

  try {
    const result = await generateText({
      model,
      messages,
      ...generateConfig,
    });

    return result.text.trim();
  } catch (error) {
    return `Error generating haiku: ${error}`;
  }
}

async function evaluateHaiku(haiku: string): Promise<string> {
  const content = `Evaluate this haiku. For a "good_enough" rating, it must:

    1. Contain the word "cat"
    2. Be three lines
    3. Generally follow 5-7-5 syllable pattern
    4. Be about cats

    Haiku to evaluate:
    ${haiku}

    Return EXACTLY "good_enough" if the requirements are met.
    Otherwise, return ONE short sentence about what needs to be fixed.`;

  try {
    const result = await generateText({
      model,
      messages: [{ role: "user", content }],
    });

    return result.text.trim();
  } catch (error) {
    return `Error evaluating haiku: ${error}`;
  }
}

// Console display functions
const display = {
  header: (text: string) => {
    console.log(chalk.cyan("\n" + "=".repeat(50)));
    console.log(chalk.cyan(text.padStart(25 + text.length / 2)));
    console.log(chalk.cyan("=".repeat(50)));
  },

  step: (text: string) => console.log(chalk.yellow(`\n▶ ${text}`)),

  haiku: (haiku: string) => {
    console.log(chalk.green("\nGenerated Haiku:"));
    haiku.split("\n").forEach((line) => {
      console.log(chalk.white(line.padStart(25 + line.length / 2)));
    });
  },

  evaluation: (evaluation: string) => {
    if (evaluation.trim() === "good_enough") {
      console.log(chalk.green("\nEvaluation: Perfect! ✨"));
    } else {
      console.log(chalk.yellow("\nEvaluation Feedback:"));
      console.log(chalk.white(evaluation));
    }
  },

  success: (text: string) => console.log(chalk.green(`\n${text}`)),
  error: (text: string) => console.log(chalk.red(`\n${text}`)),
  welcome: () =>
    console.log(chalk.cyan("\n🐱 Welcome to the Cat Haiku Generator! 🐱")),
};

async function waitForEnter(prompt: string): Promise<void> {
  return new Promise((resolve) => {
    console.log(chalk.yellow(`\n${prompt}...`));
    stdin.once("data", () => {
      resolve();
    });
  });
}

async function getUserInput(prompt: string): Promise<string> {
  return new Promise((resolve) => {
    console.log(chalk.cyan(`\n${prompt}: `));
    stdin.once("data", (data) => {
      resolve(data.toString().trim());
    });
  });
}

async function main() {
  try {
    display.welcome();
    display.header("Cat Haiku Generator");

    const prompt = await getUserInput("Please provide a theme or inspiration");
    await waitForEnter("Press Enter to start generating");

    let feedback: string | undefined;
    let previousHaiku: string | undefined;
    let iteration = 1;
    const maxIterations = 7;

    while (iteration <= maxIterations) {
      display.header(`Iteration ${iteration}/${maxIterations}`);

      // Reset feedback and previousHaiku if starting fresh
      if (iteration === 1) {
        feedback = undefined;
        previousHaiku = undefined;
      }

      display.step("Generating haiku...");
      await new Promise((resolve) => setTimeout(resolve, 500));
      const haiku = await generateHaiku(prompt, feedback, previousHaiku);
      display.haiku(haiku);

      await waitForEnter("Press Enter to evaluate");

      display.step("Evaluating haiku...");
      await new Promise((resolve) => setTimeout(resolve, 500));
      const evaluation = await evaluateHaiku(haiku);
      display.evaluation(evaluation);

      if (evaluation.trim() === "good_enough") {
        display.success("🎉 Success! Created a perfect cat haiku! 🐱");
        display.header("Final Haiku");
        display.haiku(haiku);
        break;
      }

      feedback = evaluation;
      previousHaiku = haiku;
      iteration++;

      if (iteration <= maxIterations) {
        await waitForEnter("Press Enter for next version");
      } else {
        display.error(
          "⚠️  Reached maximum iterations. Here's the last attempt:"
        );
        display.haiku(haiku);
      }
    }

    await waitForEnter("Press Enter to exit");
    exit(0);
  } catch (error) {
    display.error(`An error occurred: ${error}`);
    exit(1);
  }
}

// Handle Ctrl+C
process.on("SIGINT", () => {
  display.error("\nProgram terminated by user.");
  exit(0);
});

main();
