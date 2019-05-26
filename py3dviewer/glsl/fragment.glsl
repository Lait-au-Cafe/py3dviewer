#version 330 core
in vec4 g_position;
in vec3 g_normal;
in vec2 g_uv_coord;
uniform sampler2D sampler;

out vec4 f_color;

uniform struct LightSource {
	vec4 position;
	vec3 ambient;
	vec3 diffuse;
	vec3 specular;
} light_source;

struct Material {
	vec3 emission;
	vec3 ambient;
	vec3 diffuse;
	vec3 specular;
	float shininess;
};

void main(){
	Material material;
	material.emission = vec3(0.0, 0.0, 0.0);
	material.ambient  = texture(sampler, g_uv_coord).rgb;
	material.diffuse  = texture(sampler, g_uv_coord).rgb;
	material.specular = vec3(1.0, 1.0, 1.0);
	material.shininess = 100.0;

	vec3 col_em = material.emission;
	vec3 col_amb = material.ambient * light_source.ambient;

	vec3 light = normalize(
		(light_source.position * g_position.w - light_source.position.w * g_position).xyz);
	float diffuse = max(dot(light, g_normal), 0.0);
	vec3 col_diff = diffuse * material.diffuse * light_source.diffuse;

	vec3 view = -normalize(g_position.xyz);
	vec3 halfway = normalize(light + view);
	float specular = pow(max(dot(g_normal, halfway), 0.0), material.shininess);
	vec3 col_spec = specular * material.specular * light_source.specular;

	if(g_normal.z < 0) {
		f_color = vec4((0.1 * col_amb + col_diff + 0.3 * col_spec).rgb, 1.0);
	}
	else {
		f_color = vec4(1.0, 0.0, 1.0, 1.0);
	}
}
