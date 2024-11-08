// Handles claim parsing logic
// parseController.js
import { Configuration, OpenAIApi } from 'openai';

const configuration = new Configuration({
  apiKey: process.env.OPENAI_API_KEY, // Make sure your key is in environment variables
});

const openai = new OpenAIApi(configuration);

export const parseClaims = async (text) => {
  try {
    const response = await openai.createChatCompletion({
      model: 'gpt-4', // Use GPT-4 for better parsing
      messages: [
        {
          role: 'system',
          content: 'You are an assistant that extracts claims from text.',
        },
        {
          role: 'user',
          content: `Extract all the claims from the following text:\n\n${text}`,
        },
      ],
      temperature: 0.2, // Lower temperature for deterministic results
    });

    const claims = response.data.choices[0]?.message?.content;
    return claims ? claims.trim().split('\n') : [];
  } catch (error) {
    console.error('Error parsing claims:', error);
    throw new Error('Failed to parse claims');
  }
};
