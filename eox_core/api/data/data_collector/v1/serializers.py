from rest_framework import serializers

class DataCollectorSerializer(serializers.Serializer):
    """
    Serializer for the DataCollectorView API.

    Validates the incoming payload for the data collection endpoint.

    Fields:
        destination_url (str): The URL where the results should be sent.
    """
    destination_url = serializers.URLField(
        required=True,
        help_text="The API endpoint where the results will be sent."
    )
    token_generation_url = serializers.URLField(
        required=True,
        help_text="The API endpoint where the results will be sent."
    )
