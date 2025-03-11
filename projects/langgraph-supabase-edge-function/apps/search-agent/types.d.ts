declare module "readline" {
  interface ReadLineOptions {
    input: NodeJS.ReadableStream;
    output: NodeJS.WritableStream;
  }

  interface Interface {
    question(query: string, callback: (answer: string) => void): void;
    close(): void;
  }

  function createInterface(options: ReadLineOptions): Interface;

  export { createInterface };
  export default { createInterface };
}

declare module "process" {
  const stdin: NodeJS.ReadableStream;
  const stdout: NodeJS.WritableStream;

  export { stdin, stdout };
}
