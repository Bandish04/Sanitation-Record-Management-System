from rest_framework import serializers

from .models import TitrationLimit


class TitrationLimitSerializer(serializers.ModelSerializer):

    class Meta:
        model = TitrationLimit
        fields = [
            "id",
            "plant",
            "titration_type",
            "min_value",
            "max_value",
            "active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate(self, data):

        min_value = data.get(
            "min_value",
            self.instance.min_value if self.instance else None,
        )

        max_value = data.get(
            "max_value",
            self.instance.max_value if self.instance else None,
        )

        if min_value is None:
            raise serializers.ValidationError(
                {
                    "min_value": (
                        "Minimum value is required."
                    )
                }
            )

        if max_value is None:
            raise serializers.ValidationError(
                {
                    "max_value": (
                        "Maximum value is required."
                    )
                }
            )

        if min_value >= max_value:
            raise serializers.ValidationError(
                {
                    "max_value": (
                        "Maximum value must be greater "
                        "than minimum value."
                    )
                }
            )

        return data