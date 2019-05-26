#version 330 core
layout(location = 0) in vec3 position;
layout(location = 1) in vec2 uv_coord;

uniform mat4 mv_matrix;
uniform mat4 p_matrix;

out vec4 v_position;
out vec2 v_uv_coord;

void main(){
	v_position = mv_matrix * vec4(position, 1);
	gl_Position = p_matrix * v_position;
	v_uv_coord = uv_coord;
}
