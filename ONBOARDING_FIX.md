# Fixing Onboarding Process Issues

If you're experiencing issues with the onboarding process not prompting for API keys or models, follow these steps to fix the problem:

## Option 1: Use the Fix Script

We've created a script that will reset your configuration and allow the onboarding process to run properly:

```bash
# Run the fix script
python fix_onboarding.py

# Then run the onboarding process
python run_exo.py --onboard
```

## Option 2: Manual Fix

If you prefer to fix the issue manually, you can:

1. Delete or rename your existing configuration files:

```bash
# Backup existing config files
mv ~/.exo/config.json ~/.exo/config.json.bak
mv ~/.exo/mcp_servers.json ~/.exo/mcp_servers.json.bak
```

2. Run the onboarding process:

```bash
python run_exo.py --onboard
```

## What Was Fixed

The issue was that the onboarding process wasn't prompting for API keys if they were already set in the configuration file, even if they were empty or invalid. We've updated the code to:

1. Add a `force` parameter to the `gather_env_vars` and `run_onboarding` methods
2. Update the main.py file to pass `force=True` when the `--onboard` flag is used
3. Created a fix script to reset the configuration files

These changes ensure that when you run `python run_exo.py --onboard`, you'll be prompted for all API keys, even if they're already set in the configuration file.

## Google API Key Support

We've also added support for Google API keys, which allows you to use Google's Gemini models alongside OpenAI and Anthropic models. The onboarding process will now prompt for:

- OpenAI API key
- Anthropic API key
- Google API key
- OpenRouter API key
- Ollama configuration

## Testing the Fix

After applying the fix, you can test that the onboarding process is working correctly by running:

```bash
python run_exo.py --onboard
```

You should be prompted for all API keys, even if they're already set in the configuration file.
