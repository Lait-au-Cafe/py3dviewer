#version 330 core

layout(triangles) in;
layout(triangle_strip, max_vertices=3) out;

in vec4 v_position[];
in vec2 v_uv_coord[];

out vec2 g_uv_coord;
out vec4 g_position;
out vec3 g_normal;

void main() {
	vec3 e0 = (gl_in[1].gl_Position - gl_in[0].gl_Position).xyz;
	vec3 e1 = (gl_in[2].gl_Position - gl_in[0].gl_Position).xyz;
	vec3 n = normalize(cross(e1, e0));

	for(int i = 0; i < gl_in.length(); i++) {
		gl_Position = gl_in[i].gl_Position;
		g_normal = n;
		g_position = v_position[i];
		g_uv_coord = v_uv_coord[i];
		EmitVertex();
	}

	EndPrimitive();
}
