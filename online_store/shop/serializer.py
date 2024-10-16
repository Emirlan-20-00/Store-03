from rest_framework import serializers
from .models import *
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProFile
        fields = ('username', 'email', 'password', 'first_name', 'last_name', 'age',
                  'date_register', 'phone_number')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = UserProFile.objects.create_user(**validated_data)
        return user

    def to_representation(self, instance):
        refresh = RefreshToken.for_user(instance)
        return {
            'user': {
                'username': instance.username,
                'email': instance.email,
            },
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Текшерилген маалыматтар туура эмес.")

    def to_representation(self, instance):
        refresh = RefreshToken.for_user(instance)
        return {
            'user': {
                'username': instance.username,
                'email': instance.email,
            },
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }


class UserProFileSerializers(serializers.ModelSerializer):
    class Meta:
        model = UserProFile
        fields = '__all__'


class UserProFileSimpleSerializers(serializers.ModelSerializer):
    class Meta:
        model = UserProFile
        fields = ['first_name', 'last_name']


class CategorySerializers(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['category_name']


class ProductPhotosSerializers(serializers.ModelSerializer):
    class Meta:
        model = ProductPhotos
        fields = ['image']


class RatingSerializers(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'


class ReviewSerializers(serializers.ModelSerializer):
    created_date = serializers.DateTimeField(format='%d-%m-%Y %H:%M')

    class Meta:
        model = Review
        fields = '__all__'


class ProductListSerializers(serializers.ModelSerializer):
    get_average_rating = serializers.SerializerMethodField()
    date = serializers.DateField(format='%d-%m-%Y')

    class Meta:
        model = Product
        fields = ['id', 'product_name', 'price', 'active', 'get_average_rating', 'date']

    def get_average_rating(self, obj):
        return obj.get_average_rating


class ProductDetailSerializers(serializers.ModelSerializer):
    category = CategorySerializers()
    ratings = RatingSerializers(many=True, read_only=True)
    product = ProductPhotosSerializers(many=True, read_only=True)
    reviews = ReviewSerializers(many=True, read_only=True)
    get_average_rating = serializers.SerializerMethodField()
    date = serializers.DateField(format='%d-%m-%Y')
    owner = UserProFileSimpleSerializers()

    class Meta:
        model = Product
        fields = ['id', 'product_name', 'product', 'description', 'category', 'price', 'active',
                  'product_video', 'get_average_rating', 'ratings', 'reviews', 'date', 'owner']

    def get_average_rating(self, obj):
        return obj.get_average_rating


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializers(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), write_only=True, source='product')

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'get_total_price']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total_price',]

    def get_total_price(self, obj):
        return obj.get_total_price()
