from decimal import Decimal

from rest_framework import serializers

from .models import SanitizerTitration, ChloragelTitration


class SanitizerTitrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = SanitizerTitration
        fields = [
            "id",
            "plant",
            "sample_volume_ml",
            "r71_drops",
            "ppm",
            "percent_vv",
            "status",
            "result_status",
            "created_by",
            "created_at",
            "updated_at",
            "submitted_at",
        ]
        read_only_fields = [
            "id",
            "sample_volume_ml",
            "ppm",
            "percent_vv",
            "status",
            "result_status",
            "created_by",
            "created_at",
            "updated_at",
            "submitted_at",
        ]

    def validate_r71_drops(self, value):
        if value < 1:
            raise serializers.ValidationError(
                "R-71 drops must be at least 1."
            )

        if value > 32:
            raise serializers.ValidationError(
                "R-71 drops cannot exceed 32."
            )

        return value

    def create(self, validated_data):
        drops = validated_data["r71_drops"]

        ppm = Decimal(drops) * Decimal("12.5")
        percent_vv = Decimal(drops) * Decimal("0.0125")

        return SanitizerTitration.objects.create(
            **validated_data,
            sample_volume_ml=Decimal("5.00"),
            ppm=ppm,
            percent_vv=percent_vv,
            status=SanitizerTitration.Status.DRAFT,
            result_status=(
                SanitizerTitration.ResultStatus.REVIEW_REQUIRED
            ),
            created_by=self.context["request"].user,
        )

    def update(self, instance, validated_data):
        drops = validated_data.get(
            "r71_drops",
            instance.r71_drops,
        )

        instance.r71_drops = drops

        # Recalculate derived values whenever drops change.
        instance.ppm = Decimal(drops) * Decimal("12.5")
        instance.percent_vv = Decimal(drops) * Decimal("0.0125")

        # Update any other writable fields.
        for attr, value in validated_data.items():
            if attr != "r71_drops":
                setattr(instance, attr, value)

        # Result limits are not configured yet.
        instance.result_status = (
            SanitizerTitration.ResultStatus.REVIEW_REQUIRED
        )

        instance.save()

        return instance


class ChloragelTitrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChloragelTitration
        fields = [
            "id",
            "plant",
            "sample_volume_ml",
            "r9_drops",
            "result_percent",
            "status",
            "result_status",
            "created_by",
            "created_at",
            "updated_at",
            "submitted_at",
        ]
        read_only_fields = [
            "id",
            "sample_volume_ml",
            "result_percent",
            "status",
            "result_status",
            "created_by",
            "created_at",
            "updated_at",
            "submitted_at",
        ]

    def validate_r9_drops(self, value):
        if value < 1:
            raise serializers.ValidationError(
                "R-9 drops must be at least 1."
            )

        if value > 50:
            raise serializers.ValidationError(
                "R-9 drops cannot exceed 50."
            )

        return value

    def create(self, validated_data):
        drops = validated_data["r9_drops"]

        result_percent = Decimal(drops) * Decimal("0.198")

        return ChloragelTitration.objects.create(
            **validated_data,
            sample_volume_ml=Decimal("15.00"),
            result_percent=result_percent,
            status=ChloragelTitration.Status.DRAFT,
            result_status=(
                ChloragelTitration.ResultStatus.REVIEW_REQUIRED
            ),
            created_by=self.context["request"].user,
        )

    def update(self, instance, validated_data):
        drops = validated_data.get(
            "r9_drops",
            instance.r9_drops,
        )

        instance.r9_drops = drops

        # Recalculate derived value whenever drops change.
        instance.result_percent = Decimal(drops) * Decimal("0.198")

        # Update any other writable fields.
        for attr, value in validated_data.items():
            if attr != "r9_drops":
                setattr(instance, attr, value)

        # Result limits are not configured yet.
        instance.result_status = (
            ChloragelTitration.ResultStatus.REVIEW_REQUIRED
        )

        instance.save()

        return instance