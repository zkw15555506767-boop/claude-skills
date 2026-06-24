import { SDKLLMProvider } from './src/llm-provider.js';

process.env.ANTHROPIC_BASE_URL = "https://api.minimaxi.com/anthropic";
process.env.ANTHROPIC_API_KEY = "sk-cp-Xukhsq_j22CuVCbGVQas3GVqDOObwmwKVWV2Cp0H5sKQ5_4W13KxmLX7uhPx4PADdZ6nT4lfCHLDURUt1smoWxNbOBngp_68YFdBYmcR5rAHB7yR3gqKdm0";
process.env.ANTHROPIC_AUTH_TOKEN = "sk-cp-Xukhsq_j22CuVCbGVQas3GVqDOObwmwKVWV2Cp0H5sKQ5_4W13KxmLX7uhPx4PADdZ6nT4lfCHLDURUt1smoWxNbOBngp_68YFdBYmcR5rAHB7yR3gqKdm0";
process.env.CTI_DEFAULT_MODEL = "MiniMax-M2.5";
process.env.CTI_ENV_ISOLATION = "inherit";

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

        // @ts-ignore
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
