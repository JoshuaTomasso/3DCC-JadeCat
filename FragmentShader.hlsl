// an ultra simple hlsl fragment shader
#pragma pack_matrix(row_major)

cbuffer CameraMatrices : register(b0)
{
    float4x4 viewMatrix;
    float4x4 projectionMatrix;
    float4 lightDirection;
    float4 lightColor;
    float4 cameraPosition;
}

// Hard-coded material values as shown in the image
static float4 diffuse = { 0, 0.75f, 0, 0 };
static float4 specular = { 1, 1, 1, 1 };
static float4 ambient = { 0.1f, 0.1f, 0.1f, 1 };
static float4 emissive = { -0.25f, -0.25f, -0.25f, 1 };
static float Ns = 100;

struct PSInput
{
    float4 position : SV_POSITION;
    float3 normal : NORMAL;
    float2 texCoord : TEXCOORD0;
    float4 tangent : TANGENT;
    float3 worldPos : TEXCOORD1;
};

float4 main(PSInput input) : SV_TARGET
{
    // Normalize the interpolated normal
    float3 normal = normalize(input.normal);
    
    // Calculate the light vector (opposite of light direction)
    float3 lightVector = -normalize(lightDirection.xyz);
    
    // Calculate the view vector (from point to camera)
    float3 viewVector = normalize(cameraPosition.xyz - input.worldPos);
    
    // Calculate the halfway vector for Blinn-Phong
    float3 halfwayVector = normalize(lightVector + viewVector);
    
    // Calculate the diffuse factor (Lambert's cosine law)
    float diffuseFactor = max(dot(normal, lightVector), 0.0);
    
    // Calculate the specular factor (Blinn-Phong)
    float specularFactor = pow(max(dot(normal, halfwayVector), 0.0), Ns);
    
    // Calculate the final color
    float3 ambientColor = ambient.xyz;
    float3 diffuseColor = diffuse.xyz * diffuseFactor * lightColor.xyz;
    float3 specularColor = specular.xyz * specularFactor * lightColor.xyz;
    float3 emissiveColor = emissive.xyz;
    
    // Combine all lighting components
    float3 finalColor = ambientColor + diffuseColor + specularColor + emissiveColor;
    
    return float4(finalColor, 1.0);
}