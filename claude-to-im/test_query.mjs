import { SDKLLMProvider } from './dist/llm-provider.js';
import dotenv from 'dotenv';

dotenv.config({ path: '/Users/wow/.claude-to-im/config.env' });

const pendingPerms = { waitFor: async () => ({ behavior: 'allow' }) };
const provider = new SDKLLMProvider(pendingPerms, '/usr/local/bin/claude', true);

async function run() {
  console.log("Starting SDK query test...");
  try {
    const stream = provider.streamChat({
      prompt: "Hello, this is a test from direct script",
      model: process.env.CTI_DEFAULT_MODEL || "MiniMax-M2.5",
      workingDirectory: "/Users/wow",
      permissionMode: "default"
    });

    // Convert ReadableStream to async iterable for loop
    const reader = stream.getReader();
    while (true) {
      const { done, value } = await reader.read();
      if (done) {
        console.log("Stream finished.");
        break;
      }
      console.log("Chunk:", value);
    }
  } catch (err) {
    console.error("TEST SCRIPT CATCH:", err);
  }
}

run().catch(console.error);
