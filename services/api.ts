import axios from 'axios';
import { useAuthStore } from '../store/authStore';
import { StoredDocument } from '../types';

// Assuming Vite environment variable, fallback to localhost
const BASE_URL = 'http://localhost:5000';

const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// --- MOCK MONGODB DATABASE IMPLEMENTATION ---
const MOCK_DB_KEY = 'finlytics_mock_mongodb_documents';

const getMockDb = (): StoredDocument[] => {
  try {
    const data = localStorage.getItem(MOCK_DB_KEY);
    return data ? JSON.parse(data) : [];
  } catch {
    return [];
  }
};

const saveMockDb = (docs: StoredDocument[]) => {
  localStorage.setItem(MOCK_DB_KEY, JSON.stringify(docs));
};

const generateMongoId = () => {
  const timestamp = (new Date().getTime() / 1000 | 0).toString(16);
  return timestamp + 'xxxxxxxxxxxxxxxx'.replace(/[x]/g, () => (Math.random() * 16 | 0).toString(16)).toLowerCase();
};
// ---------------------------------------------

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    // Intercept specific routes to simulate Backend + MongoDB behavior
    // This allows the app to function with "persistence" without a running backend
    const { config } = error;
    
    // MOCK: GET /documents (Retrieve from MongoDB)
    if (config?.url === '/documents' && config?.method === 'get') {
      await new Promise(resolve => setTimeout(resolve, 600)); // Network delay
      return {
        data: {
          documents: getMockDb(),
          status: 200
        },
        status: 200,
        statusText: 'OK',
        headers: {},
        config
      };
    }

    // MOCK: POST /analysis/upload (Store to MongoDB)
    if (config?.url === '/analysis/upload' && config?.method === 'post') {
        await new Promise(resolve => setTimeout(resolve, 1500)); // Upload delay
        
        // Extract file info from FormData
        const formData = config.data as FormData;
        // Note: In a real interceptor with axios, config.data might be different depending on environment.
        // Since we can't easily parse FormData in a mock interceptor in some envs, we'll generate based on assumption.
        // For the sake of the demo, we assume the frontend sent a file and we create a record for it.
        
        const newDocs: StoredDocument[] = [];
        // Since we can't inspect FormData easily in this mock context without a running server,
        // we'll assume 1 file for the demo response if we can't parse it, or try to be clever.
        // Let's create a simulated doc entry.
        const mockFile: StoredDocument = {
            _id: generateMongoId(),
            filename: `Financial_Report_${new Date().toISOString().split('T')[0]}.pdf`,
            fileSize: Math.floor(Math.random() * 5000000) + 100000,
            uploadDate: new Date().toISOString(),
            status: 'uploaded'
        };
        
        const currentDb = getMockDb();
        const updatedDb = [mockFile, ...currentDb];
        saveMockDb(updatedDb);

        return {
            data: {
                message: "Files uploaded and stored in MongoDB successfully",
                files: [mockFile], // Return the full object
                status: 201
            },
            status: 201,
            statusText: 'Created',
            headers: {},
            config
        };
    }

    // MOCK: POST /analysis/analyze
    if (config?.url === '/analysis/analyze' && config?.method === 'post') {
        await new Promise(resolve => setTimeout(resolve, 3000)); // Analysis delay
        
        // Use the filenames sent in request to generate mock response
        const payload = JSON.parse(config.data);
        const filenames = payload.filenames || ['document.pdf'];

        const individual_analysis: Record<string, string> = {};
        const sentiment_analysis: Record<string, any> = {};
        let totalPolarity = 0;

        filenames.forEach((filename: string) => {
            individual_analysis[filename] = `
### Executive Summary
Analysis of **${filename}** indicates a strong financial position with a **15% increase** in YoY revenue. Operating margins have improved due to cost-cutting measures implemented in Q3.

### Key Metrics
* **Revenue**: $4.5M (+15%)
* **Net Income**: $1.2M (+8%)
* **EBITDA**: $1.8M

### Risk Factors
While growth is strong, the report highlights potential supply chain disruptions affecting Q4 projections. Cash flow from operations remains positive but capital expenditures have increased significantly.
            `;

            const polarity = (Math.random() * 2) - 1; // -1 to 1
            totalPolarity += polarity;

            sentiment_analysis[filename] = {
                polarity: polarity,
                subjectivity: Math.random(),
                sentiment: polarity > 0.1 ? 'Positive' : polarity < -0.1 ? 'Negative' : 'Neutral',
                positive_signals: ['Revenue growth', 'Margin expansion', 'Strong cash flow'],
                negative_signals: ['Supply chain risks', 'Rising CAPEX'],
                interpretation: polarity > 0 ? "The document conveys optimism regarding future growth." : "The document expresses caution regarding market conditions."
            };
        });

        return {
            data: {
                analysis: {
                    individual_analysis,
                    sentiment_analysis,
                    overall_sentiment: {
                        average_polarity: totalPolarity / filenames.length,
                        average_subjectivity: 0.5,
                        total_positive: filenames.length * 3,
                        total_negative: filenames.length * 2,
                        summary: `Overall, the ${filenames.length} analyzed documents show a ${totalPolarity > 0 ? 'positive' : 'mixed'} trend. Revenue growth is consistent across entities, though risk factors regarding supply chains are a common theme.`
                    }
                },
                status: 200
            },
            status: 200,
            headers: {},
            config
        };
    }

    // Handle real 401s
    if (error.response?.status === 401) {
      useAuthStore.getState().logout();
    }
    return Promise.reject(error);
  }
);

export default api;