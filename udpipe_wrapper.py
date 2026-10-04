"""
Wrapper module for using udpipe2_client functions programmatically.
"""
import argparse
from udpipe2_client import perform_request, process

class UDPipeWrapper:
    """A wrapper class to use UDPipe functionality programmatically."""

    
    def __init__(self, service="https://lindat.mff.cuni.cz/services/udpipe/api"):
        self.service = service
    
    def get_models(self):
        """Get list of available models."""
        # Create a mock args object
        args = argparse.Namespace()
        args.service = self.service
        
        response = perform_request(self.service, "models")
        models = []
        if "models" in response:
            models = response["models"]
        
        default_model = response.get("default_model", None)
        return models, default_model
    
    def parse_text(self, text, model=None, input_format="horizontal", output_format="conllu", 
                   tokenizer="default", parser="default", tagger="default"):
        """
        Parse text using UDPipe.
        
        Args:
            text (str): The text to parse
            model (str): Model to use (None for default). Can be only several first words of model name, ISO 639-1, or ISO 639-2 code of a language. If available, newest model for the requested language is used.
            input_format (str): Input format ("conllu" / "generic_tokenizer" / "horizontal" / "vertical", default: "horizontal")
            output_format (str): Output format ("conllu" / "horizontal" / "matxin" / "plaintext" / "vertical", default: "conllu")
            tokenizer (str): Tokenizer options. The default option is "default"
            parser (str): Parser options. The default option is "default"
            tagger (str): Tagger options. The default option is "default"
    
        Returns:
            str: Parsed output
        """
        # Create a mock args object
        args = argparse.Namespace()
        args.service = self.service
        args.input = input_format
        args.output = output_format
        args.model = model
        args.tokenizer = tokenizer
        args.parser = parser
        args.tagger = tagger
        
        return process(args, text)
    
    def parse_file(self, input_file_path, output_file_path=None, model=None, 
                   input_format="horizontal", output_format="conllu",
                   tokenizer="default", parser="default", tagger="default"):
        """
        Parse a file using UDPipe.
        
        Args:
            input_file_path (str): Path to input file
            output_file_path (str): Path to output file (None for stdout)
            model (str): Model to use (None for default). Can be only several first words of model name, ISO 639-1, or ISO 639-2 code of a language. If available, newest model for the requested language is used.
            input_format (str): Input format ("conllu" / "generic_tokenizer" / "horizontal" / "vertical", default: "horizontal")
            output_format (str): Output format ("conllu" / "horizontal" / "matxin" / "plaintext" / "vertical", default: "conllu")
            tokenizer (str): Tokenizer options. The default option is "default"
            parser (str): Parser options. The default option is "default"
            tagger (str): Tagger options. The default option is "default"
        
        Returns:
            str: Parsed output
        """
        # Read input file
        with open(input_file_path, "r", encoding="utf-8-sig", newline="") as f:
            text = f.read()
        
        # Parse text
        result = self.parse_text(text, model, input_format, output_format, 
                               tokenizer, parser, tagger)
        
        # Write to output file if specified
        if output_file_path:
            with open(output_file_path, "w", encoding="utf-8") as f:
                f.write(result)
        
        return result


# Example usage functions
def example_usage():
    """Example of how to use the UDPipeWrapper."""
    
    # Initialize wrapper
    udpipe = UDPipeWrapper()
    
    # Get available models
    models, default_model = udpipe.get_models()
    print(f"Available models: {list(models.keys())[:5]}...")  # Show first 5 models
    print(f"Default model: {default_model}")
    
    # Parse some text
    sample_text = "Hello world. This is a test sentence."
    result = udpipe.parse_text(
        text=sample_text,
        model="eng",  # or use None for default
        input_format="horizontal",
        output_format="conllu"
    )
    
    print("\nParsed text:")
    print(result)
    
    return result


if __name__ == "__main__":
    example_usage()