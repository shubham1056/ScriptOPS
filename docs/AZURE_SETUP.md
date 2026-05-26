# Azure OpenAI Setup

1. Create an **Azure OpenAI** resource in the Azure portal.
2. Deploy the **GPT-5** model — name your deployment (e.g. `gpt-5-sop`).
3. Copy the **endpoint**, **API key**, **deployment name**, and **API version**.
4. Populate `apps/api/.env`:

```env
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_DEPLOYMENT=gpt-5-sop
AZURE_OPENAI_API_VERSION=2024-10-21
```

5. (Optional) Provision **Azure Blob Storage** for file uploads.

```env
STORAGE_BACKEND=azure_blob
AZURE_STORAGE_CONNECTION_STRING=...
AZURE_STORAGE_CONTAINER=transcribeop
```
