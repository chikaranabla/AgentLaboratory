"""
Google Gemini API Integration Module

This module provides inference capabilities using Google's Gemini API,
following the pattern of the existing inference.py module.
"""

import time
import os
from typing import Optional, Dict
import google.generativeai as genai


# Token usage tracking
TOKENS_IN = {}
TOKENS_OUT = {}


def curr_cost_est() -> float:
    """
    Calculate current estimated cost based on token usage.
    
    Returns:
        Estimated cost in USD
    """
    # Gemini pricing (as of 2024)
    # gemini-pro: $0.00025 per 1K characters for input, $0.0005 per 1K characters for output
    # Approximation: 1 token ≈ 4 characters
    costmap_in = {
        "gemini-pro": 0.00025 / 1000 * 4,  # per token
        "gemini-1.5-pro": 0.00125 / 1000 * 4,
        "gemini-1.5-flash": 0.000075 / 1000 * 4,
    }
    costmap_out = {
        "gemini-pro": 0.0005 / 1000 * 4,
        "gemini-1.5-pro": 0.005 / 1000 * 4,
        "gemini-1.5-flash": 0.0003 / 1000 * 4,
    }
    
    total_cost = 0.0
    for model in TOKENS_IN:
        if model in costmap_in:
            total_cost += costmap_in[model] * TOKENS_IN[model]
    for model in TOKENS_OUT:
        if model in costmap_out:
            total_cost += costmap_out[model] * TOKENS_OUT[model]
    
    return total_cost


def query_gemini(
    model_str: str,
    prompt: str,
    system_prompt: str,
    gemini_api_key: Optional[str] = None,
    tries: int = 5,
    timeout: float = 5.0,
    temp: Optional[float] = None,
    max_tokens: Optional[int] = None,
    print_cost: bool = True
) -> str:
    """
    Query Google Gemini API for text generation.
    
    Args:
        model_str: Model name (e.g., "gemini-pro", "gemini-1.5-pro", "gemini-1.5-flash")
        prompt: User prompt/query
        system_prompt: System instructions/context
        gemini_api_key: Google Gemini API key
        tries: Number of retry attempts
        timeout: Timeout between retries in seconds
        temp: Temperature for generation (0.0-1.0)
        max_tokens: Maximum tokens to generate
        print_cost: Whether to print cost estimation
        
    Returns:
        Generated text response
        
    Raises:
        Exception: If all retry attempts fail
    """
    # Get API key from environment if not provided
    if gemini_api_key is None:
        gemini_api_key = os.getenv('GEMINI_API_KEY')
    
    if gemini_api_key is None:
        raise ValueError("Gemini API key not provided. Set GEMINI_API_KEY environment variable or pass gemini_api_key parameter.")
    
    # Configure Gemini
    genai.configure(api_key=gemini_api_key)
    
    # Map model names to Gemini model names
    model_mapping = {
        "gemini-pro": "gemini-2.0-flash-lite",
        "gemini-1.5-pro": "gemini-1.5-pro",
        "gemini-1.5-flash": "gemini-1.5-flash",
        "gemini-2.0-flash-lite": "gemini-2.0-flash-lite",
        "gemini": "gemini-2.0-flash-lite",  # Default
    }
    
    gemini_model_name = model_mapping.get(model_str, "gemini-2.0-flash-lite")
    
    # Set generation config
    generation_config = {}
    if temp is not None:
        generation_config["temperature"] = temp
    if max_tokens is not None:
        generation_config["max_output_tokens"] = max_tokens
    
    # Combine system prompt and user prompt
    # Gemini doesn't have a separate system prompt, so we prepend it to the user message
    combined_prompt = f"{system_prompt}\n\n{prompt}"
    
    # Retry loop
    for attempt in range(tries):
        try:
            # Create model instance
            model = genai.GenerativeModel(
                model_name=gemini_model_name,
                generation_config=generation_config if generation_config else None
            )
            
            # Generate response
            response = model.generate_content(combined_prompt)
            
            # Extract text from response
            if hasattr(response, 'text'):
                answer = response.text
            elif hasattr(response, 'parts'):
                answer = ''.join([part.text for part in response.parts])
            else:
                answer = str(response)
            
            # Track token usage (approximation)
            # Gemini API doesn't provide exact token counts, so we estimate
            input_chars = len(combined_prompt)
            output_chars = len(answer)
            
            # Approximate: 1 token ≈ 4 characters
            input_tokens = input_chars // 4
            output_tokens = output_chars // 4
            
            if model_str not in TOKENS_IN:
                TOKENS_IN[model_str] = 0
                TOKENS_OUT[model_str] = 0
            
            TOKENS_IN[model_str] += input_tokens
            TOKENS_OUT[model_str] += output_tokens
            
            # Print cost estimation
            if print_cost:
                cost = curr_cost_est()
                print(f"Current experiment cost = ${cost:.4f} (Approximate, Gemini)")
            
            return answer
            
        except Exception as e:
            error_msg = str(e)
            print(f"Gemini API Exception (attempt {attempt + 1}/{tries}): {error_msg}")
            
            # Check for specific error types
            if "quota" in error_msg.lower() or "rate" in error_msg.lower():
                print("Rate limit or quota exceeded. Waiting longer...")
                time.sleep(timeout * (attempt + 1) * 2)
            elif "safety" in error_msg.lower():
                print("Safety filter triggered. Trying again...")
                time.sleep(timeout)
            else:
                time.sleep(timeout)
            
            # If this is the last attempt, raise the exception
            if attempt == tries - 1:
                raise
            
            continue
    
    raise Exception(f"Max retries ({tries}) exceeded: timeout")


def query_model_gemini(
    model_str: str,
    prompt: str,
    system_prompt: str,
    gemini_api_key: Optional[str] = None,
    tries: int = 5,
    timeout: float = 5.0,
    temp: Optional[float] = None,
    max_tokens: Optional[int] = 2048,
    print_cost: bool = True
) -> str:
    """
    Unified interface for querying Gemini models.
    Compatible with the existing query_model interface from inference.py
    
    Args:
        model_str: Model name
        prompt: User prompt
        system_prompt: System instructions
        gemini_api_key: API key
        tries: Retry attempts
        timeout: Timeout between retries
        temp: Temperature
        max_tokens: Maximum tokens to generate
        print_cost: Whether to print cost
        
    Returns:
        Generated response text
    """
    return query_gemini(
        model_str=model_str,
        prompt=prompt,
        system_prompt=system_prompt,
        gemini_api_key=gemini_api_key,
        tries=tries,
        timeout=timeout,
        temp=temp,
        max_tokens=max_tokens,
        print_cost=print_cost
    )


def get_token_usage() -> Dict[str, Dict[str, int]]:
    """
    Get current token usage statistics.
    
    Returns:
        Dictionary with input and output token counts per model
    """
    return {
        "input": dict(TOKENS_IN),
        "output": dict(TOKENS_OUT)
    }


def reset_token_usage():
    """Reset token usage counters."""
    global TOKENS_IN, TOKENS_OUT
    TOKENS_IN = {}
    TOKENS_OUT = {}


# Example usage
if __name__ == "__main__":
    # Test the Gemini API
    test_response = query_gemini(
        model_str="gemini-pro",
        prompt="What is artificial intelligence?",
        system_prompt="You are a helpful AI assistant.",
        temp=0.7
    )
    print("Test Response:", test_response)
    print("Token Usage:", get_token_usage())
    print(f"Total Cost: ${curr_cost_est():.4f}")

