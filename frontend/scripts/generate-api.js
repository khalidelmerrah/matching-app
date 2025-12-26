import { execSync } from 'child_process';

const BACKEND_URL = 'http://localhost:8000/openapi.json';
const OUTPUT_FILE = './src/lib/api-types.ts';

try {
    console.log(`Generating types from ${BACKEND_URL}...`);
    execSync(`npx openapi-typescript ${BACKEND_URL} -o ${OUTPUT_FILE}`);
    console.log('Types generated successfully.');
} catch (error) {
    console.error('Failed to generate types:', error);
    process.exit(1);
}
