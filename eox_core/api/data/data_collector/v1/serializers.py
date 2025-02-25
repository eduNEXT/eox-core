from rest_framework import serializers


class DataCollectorSerializer(serializers.Serializer):
    """
    Serializer for the DataCollectorView API.

    This serializer is used to validate the payload for the data collection endpoint.
    It ensures that the required URLs are provided for sending collected data and 
    generating authentication tokens.
    
    Fields:
        destination_url (str): The URL where the results should be sent.
        token_generation_url (str): The API endpoint used to generate authentication tokens.
    """
    destination_url = serializers.URLField(
        required=True,
        help_text="The API endpoint where the results will be sent."
    )
    token_generation_url = serializers.URLField(
        required=True,
        help_text="The API endpoint where the results will be sent."
    )
