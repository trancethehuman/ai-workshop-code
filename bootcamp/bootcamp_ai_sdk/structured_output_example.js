import { generateObject } from "ai";
import { z } from "zod";
import { recipe } from "./recipe.js";
import { createOpenAI } from "@ai-sdk/openai";
import * as dotenv from "dotenv";

dotenv.config();

const openai = createOpenAI({
  compatibility: "strict",
});

const model = openai("gpt-4o-mini");

// input: a website html

// output:
const RecipeSchema = z.object({
  ingredients: z.array(z.string()),
  steps: z.array(z.string()),
  time: z.number(),
  effort: z.string(),
});

const result = await generateObject({
  model: model,
  defaultObjectGenerationMode: "strict",
  schema: RecipeSchema,
  prompt: `Extract recipe information from the provided HTML. 
    Return a structured JSON object with:
    - ingredients (list of strings)
    - steps (list of strings)
    - time in seconds (number)
    - effort level (string)
    
    HTML content: ${recipe}`,
});

console.log(result.object);
