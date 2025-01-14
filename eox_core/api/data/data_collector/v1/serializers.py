from rest_framework import serializers

class DataCollectorSerializer(serializers.Serializer):
    """
    Serializer for the DataCollectorView API.

    Validates the incoming payload for the data collection endpoint.

    Fields:
        query_file_content (str): The content of the query file in YAML format.
        query_file_url (str): A public URL pointing to the query file.
        destination_url (str): The URL where the results should be sent.
    """
    query_file_content = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Content of the query file in YAML format."
    )
    query_file_url = serializers.URLField(
        required=False,
        allow_blank=True,
        help_text="Public URL pointing to the query file."
    )
    destination_url = serializers.URLField(
        required=True,
        help_text="The API endpoint where the results will be sent."
    )
    token_generation_url = serializers.URLField(
        required=True,
        help_text="The API endpoint where the results will be sent."
    )

    def validate(self, data):
        """
        Custom validation to ensure either 'query_file_content' or 'query_file_url' is provided.

        Args:
            data (dict): The validated data.

        Returns:
            dict: The validated data if valid.

        Raises:
            serializers.ValidationError: If neither 'query_file_content' nor 'query_file_url' is provided.
        """
        if not data.get("query_file_content") and not data.get("query_file_url"):
            raise serializers.ValidationError(
                "Either 'query_file_content' or 'query_file_url' must be provided."
            )
        return data
