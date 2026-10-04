from rest_framework import serializers


class CombinedRecordSerializer(serializers.Serializer):
    id = serializers.IntegerField()

    record_type = serializers.CharField()

    plant = serializers.IntegerField()
    plant_code = serializers.CharField()
    plant_name = serializers.CharField()

    status = serializers.CharField()

    date = serializers.DateField()

    created_by = serializers.IntegerField()
    created_by_username = serializers.CharField()

    created_at = serializers.DateTimeField()

    data = serializers.DictField()


class DailyRecordsSerializer(serializers.Serializer):
    plant = serializers.IntegerField()
    plant_code = serializers.CharField()
    plant_name = serializers.CharField()

    date = serializers.DateField()

    sanitizer_titrations = serializers.ListField()

    chloragel_titrations = serializers.ListField()

    inspections = serializers.ListField()

    atp_reports = serializers.ListField()