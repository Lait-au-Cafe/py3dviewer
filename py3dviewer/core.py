"""
@file core.py
@version 0.1.0
@author Lait-au-Cafe
@date 10/05/2019
"""
# -*- coding: utf-8 -*-
import sys
import os
import typing
import dataclasses
import numpy as np
import cv2
import OpenGL.GL as gl
import glfw
import glm
import ctypes

@dataclasses.dataclass
class CameraProperty:
    transform_matrix: glm.mat4
    clipping_distance: glm.vec2
    field_of_view: float

    def clone(self):
        """
        @fn clone()
        @brief Make a deep copy of an instance. 
        """
        return CameraProperty(
                transform_matrix = glm.mat4(self.transform_matrix), 
                clipping_distance = glm.vec2(self.clipping_distance), 
                field_of_view = self.field_of_view)

@dataclasses.dataclass
class CursorStatus:
    button: typing.Dict[int, bool]
    position: glm.vec2

class Viewer:
    """
    @class Viewer
    @brief A class which deals with the rendering of specified model. 
    @detail This class renders the model specified in the argument of constructor as model_vertices and mode_uvmap. 
    """

    """
    @var model_vertices
    @brief The list of model vertices ([X1 Y1 Z1 X2 Y2 Z2 ...]). 
    """
    model_vertices: typing.List[float]

    """
    @var model_indices
    @brief The list of model vertices ([ID1 ID2 ID3 ...]). 
    """
    model_indices: typing.List[int]

    """
    @var model_uvmap
    @brief The list of correspondence between model vertices and texture uv coordinate ([U1 V1 U2 V2 ...]). 
    """
    model_uvmap: typing.List[float]

    """
    @var window
    @brief The window object of GLFW. 
    """
    window: glfw._GLFWwindow

    """
    @var window_size
    @brief The size of the window (width, height). 
    """
    window_size: typing.Tuple[int, int]

    """
    @var camera_property
    @brief The properties of the camera. 
    """
    camera_property: CameraProperty

    """
    @var default_camera_property
    @brief The default properties of the camera. 
    """
    default_camera_property: CameraProperty

    """
    @var vertex_buffer
    @brief The ID of vertex buffer. 
    """
    vertex_buffer: np.uint32

    """
    @var index_buffer
    @brief The ID of index buffer. 
    """
    index_buffer: np.uint32

    """
    @var uv_buffer
    @brief The ID of uv buffer. 
    """
    uv_buffer: np.uint32

    """
    @var va_object
    @brief The vertext array object of OpenGL which stores model_vertices and model_uvmap. 
    """
    va_object: np.uint32

    """
    @var texture
    @brief The ID of texture in OpenGL. 
    """
    texture: int

    """
    @var shader_program
    @brief The ID of shader program in OpenGL. 
    """
    shader_program: int

    @staticmethod
    def on_error(code: int, message: str):
        """
        @fn on_error()
        @brief Callback function invoked when glfw encounters errors. 
        @param code Error code. 
        @param message Error message. 
        """
        print(f"[GLFW Error] {message} ({code})")

    @staticmethod
    def load_shader(shader_id: int, filename: str) -> bool:
        """
        @fn load_shader()
        @brief Load shader script from a file. 
        @param shader_id The ID of the shader to which the texture should be bound. 
        @param filename The filename of a shader file. 
        @return Whether the loading succeeded. 
        """
        with open(filename) as shader_file:
            shader_code = shader_file.read()
            gl.glShaderSource(shader_id, [shader_code])
            gl.glCompileShader(shader_id)

            result = gl.glGetShaderiv(shader_id, gl.GL_COMPILE_STATUS)
            if result != gl.GL_TRUE:
                print(f"[GLFW Error] {gl.glGetShaderInfoLog(shader_id)}")
                return False

        return True

    @staticmethod
    def help():
        print()
        print(":======== Window Control ========:")
        print("Esc: Close the window. ")
        print("Left-Drag: Panning. ")
        print("Right-Drag: Rotate around the origin. ")
        print("Scroll: Zoom-in/out. ")
        print("W: Move forward. ")
        print("A: Move left. ")
        print("S: Move backward. ")
        print("D: Move right. ")
        print("Shift + W: Move up. ")
        print("Shift + S: Move down. ")
        print("Up: Face up. ")
        print("Down: Face down. ")
        print("Left: Turn left. ")
        print("Right: Turn right. ")
        print("Space: Reset the camera position. ")
        print(":================================:")
        print()

    def update_model(self, 
        model_vertices: typing.List[float], 
        model_indices: typing.List[int], 
        model_uvmap: typing.List[float]):
        """
        @fn update_model()
        @brief Update the model data to be rendered. 
        @param model_vertices The list of vertices. 
        @param model_indices The list of indices. 
        @param model_uvmap The list of uvs. 
        """
        # --- Vertex buffer ---
        c_vertex_buffer = (ctypes.c_float*len(model_vertices))(*model_vertices)
        c_vertex_buffer_size = ctypes.sizeof(ctypes.c_float) * len(model_vertices)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vertex_buffer)

        if len(model_vertices) > len(self.model_vertices):
            # Reallocate memory
            gl.glBufferData(gl.GL_ARRAY_BUFFER, c_vertex_buffer, gl.GL_DYNAMIC_DRAW)
            c_vertex_buffer_size = ctypes.sizeof(ctypes.c_float) * len(model_vertices)
            size_allocated = gl.glGetBufferParameteriv(gl.GL_ARRAY_BUFFER, gl.GL_BUFFER_SIZE)

            if size_allocated != c_vertex_buffer_size:
                print("[GL Error] Failed to allocate memory for buffer. ")
                gl.glDeleteBuffers(1, self.vertex_buffer);
                sys.exit()
        else:
            # Update elements
            gl.glBufferSubData(gl.GL_ARRAY_BUFFER, 0, c_vertex_buffer_size, c_vertex_buffer)

        self.model_vertices = model_vertices

        # --- Index buffer ---
        c_index_buffer = (ctypes.c_uint32*len(model_indices))(*model_indices)
        c_index_buffer_size = ctypes.sizeof(ctypes.c_uint32) * len(model_indices)
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.index_buffer)

        if len(model_indices) > len(self.model_indices):
            # Reallocate memory
            gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, c_index_buffer, gl.GL_DYNAMIC_DRAW)
            c_index_buffer_size = ctypes.sizeof(ctypes.c_uint32) * len(model_indices)
            size_allocated = \
                gl.glGetBufferParameteriv(gl.GL_ELEMENT_ARRAY_BUFFER, gl.GL_BUFFER_SIZE)

            if size_allocated != c_index_buffer_size:
                print("[GL Error] Failed to allocate memory for buffer. ")
                gl.glDeleteBuffers(1, self.index_buffer);
                sys.exit()
        else:
            # Update elements
            gl.glBufferSubData(gl.GL_ELEMENT_ARRAY_BUFFER, 0, c_index_buffer_size, c_index_buffer)

        self.model_indices = model_indices

        # --- UV buffer ---
        c_uv_buffer = (ctypes.c_float*len(model_uvmap))(*model_uvmap)
        c_uv_buffer_size = ctypes.sizeof(ctypes.c_float) * len(model_uvmap)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.uv_buffer)

        if len(model_uvmap) > len(self.model_uvmap):
            # Reallocate memory
            gl.glBufferData(gl.GL_ARRAY_BUFFER, c_uv_buffer, gl.GL_DYNAMIC_DRAW)
            c_uv_buffer_size = ctypes.sizeof(ctypes.c_float) * len(model_uvmap)
            size_allocated = gl.glGetBufferParameteriv(gl.GL_ARRAY_BUFFER, gl.GL_BUFFER_SIZE)

            if size_allocated != c_uv_buffer_size:
                print("[GL Error] Failed to allocate memory for buffer. ")
                gl.glDeleteBuffers(1, self.uv_buffer);
                sys.exit()
        else:
            # Update elements
            gl.glBufferSubData(gl.GL_ARRAY_BUFFER, 0, c_uv_buffer_size, c_uv_buffer)

        self.model_uvmap = model_uvmap

        # unbind
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

    def update_camera_matrix(self):
        """
        @fn update_camera_matrix()
        @brief Calculate MVP matrix and upload it to GPU. 
        """
        # Calculate the perspective matrix
        perspective_matrix = glm.perspectiveFovLH_NO(
                glm.radians(self.camera_property.field_of_view), 
                self.window_size[0], self.window_size[1], 
                self.camera_property.clipping_distance[0], 
                self.camera_property.clipping_distance[1])

        # Compose MVP matrix
        mvp_matrix = perspective_matrix * self.camera_property.transform_matrix

        # Upload to uniform variable in the shader
        gl.glUseProgram(self.shader_program)
        gl.glUniformMatrix4fv(gl.glGetUniformLocation(self.shader_program, "mvp_matrix"), 
                1, gl.GL_FALSE, glm.value_ptr(mvp_matrix))

    def window_size_callback(self, window: glfw._GLFWwindow, new_width: int, new_height: int):
        """
        @fn window_size_callback()
        @brief The callback function for glfw.set_window_size_callback(). 
        @param window The ID of the window which is resized. 
        @param new_width The updated width of the window. 
        @param new_height The updated height of the window. 
        """
        # For the support of retina display, use the framebuffer size instead of the window size. 
        self.window_size = glfw.get_framebuffer_size(self.window)
        self.update_camera_matrix()
        gl.glViewport(0, 0, new_width, new_height)

    def mouse_scroll_callback(self, window: glfw._GLFWwindow, x_offset: float, y_offset: float):
        """
        @fn mouse_scroll_callback()
        @brief The callback function for glfw.set_sroll_callback(). 
        @param window The ID of the window which is resized. 
        @param x_offset The offset along x axis. 
        @param y_offset The offset along y axis. 
        """
        if y_offset != 0.:
            if y_offset > 0.:
                tmat = glm.scale(glm.mat4(1.), glm.vec3(1.25))
            else:
                tmat = glm.scale(glm.mat4(1.), glm.vec3(0.8))
            self.camera_property.transform_matrix = self.camera_property.transform_matrix * tmat
            self.update_camera_matrix()

    def display_all_instance_variables(self):
        """
        @fn display_all_instancevariables()
        @brief For developpers. List up all the instance variables. 
        """
        print(" ==== Instance Variables in Viewer ==== ")
        [print(f"{key}: {type(val)}") for key, val in vars(self).items()]
        print(" ====================================== ")

    def __init__(self, 
        window_title: str, 
        model_vertices: typing.List[float], 
        model_indices: typing.List[int], 
        model_uvmap: typing.List[float], 
        texture_filename: str):
        """
        @fn __init__()
        @brief Initialization of viewer.  
        @param model_vertices The list of vertices in the model. 
        @param model_uvmap the uvmapping which associate model_vertices with textures
        @param texture_filename The path to the texture file. 
        @param window_title The title of the window. 
        @note The format of model_vertices is [X1, Y1, Z1, X2, Y2, ...]. 
        @note The format of model_uvmap is [U1, V1, U2, V2, ...]. 
        """
        print("Initializing Viewer...")

        # set callback function on error
        glfw.set_error_callback(Viewer.on_error)

        # Initialize
        if glfw.init() != gl.GL_TRUE:
            print("[GLFW Error] Failed to initialize GLFW. ")
            sys.exit()

        #========================================
        # Prepare Window
        #========================================
        print("- Creating a window.")
        # Window hints
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)

        # Create window
        self.window_size = (640, 480)
        self.window = glfw.create_window(
                self.window_size[0],  # width
                self.window_size[1],  # height
                window_title,  # window title
                None, 
                None)

        if self.window == None:
            print("[GLFW Error] Failed to Create a window. ")
            sys.exit()

        # Create OpenGL context
        glfw.make_context_current(self.window)

        # Set background color.
        gl.glClearColor(0.0, 1.0, 1.0, 1.0)

        # Set callback functions
        glfw.set_window_size_callback(self.window, self.window_size_callback)
        glfw.set_scroll_callback(self.window, self.mouse_scroll_callback)

        #========================================
        # Prepare Buffers
        #========================================
        print("- Preparing buffers.")

        # --- Vertex buffer ---
        # Generate & bind buffer
        self.model_vertices = model_vertices
        self.vertex_buffer = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vertex_buffer)

        # Allocate memory
        c_vertex_buffer = (ctypes.c_float*len(model_vertices))(*model_vertices)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, c_vertex_buffer, gl.GL_DYNAMIC_DRAW)
        c_vertex_buffer_size = ctypes.sizeof(ctypes.c_float) * len(model_vertices)
        size_allocated = gl.glGetBufferParameteriv(gl.GL_ARRAY_BUFFER, gl.GL_BUFFER_SIZE)

        if size_allocated != c_vertex_buffer_size:
            print("[GL Error] Failed to allocate memory for buffer. ")
            gl.glDeleteBuffers(1, self.vertex_buffer);
            sys.exit()

        # --- Index buffer ---
        # Generate & bind buffer
        self.model_indices = model_indices
        self.index_buffer = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.index_buffer)

        # Allocate memory
        c_index_buffer = (ctypes.c_uint32*len(model_indices))(*model_indices)
        gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, c_index_buffer, gl.GL_DYNAMIC_DRAW)
        c_index_buffer_size = ctypes.sizeof(ctypes.c_uint32) * len(model_indices)
        size_allocated = gl.glGetBufferParameteriv(gl.GL_ELEMENT_ARRAY_BUFFER, gl.GL_BUFFER_SIZE)

        if size_allocated != c_index_buffer_size:
            print("[GL Error] Failed to allocate memory for buffer. ")
            gl.glDeleteBuffers(1, self.index_buffer);
            sys.exit()

        # --- UV buffer ---
        # Generate & bind buffer
        self.model_uvmap = model_uvmap
        self.uv_buffer = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.uv_buffer)

        # Allocate memory
        c_uv_buffer = (ctypes.c_float*len(model_uvmap))(*model_uvmap)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, c_uv_buffer, gl.GL_DYNAMIC_DRAW)
        c_uv_buffer_size = ctypes.sizeof(ctypes.c_float) * len(model_uvmap)
        size_allocated = gl.glGetBufferParameteriv(gl.GL_ARRAY_BUFFER, gl.GL_BUFFER_SIZE)

        if size_allocated != c_uv_buffer_size:
            print("[GL Error] Failed to allocate memory for buffer. ")
            gl.glDeleteBuffers(1, self.uv_buffer);
            sys.exit()

        # --- Bind to vertex array object ---
        self.va_object = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(self.va_object)

        gl.glEnableVertexAttribArray(0)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vertex_buffer)
        gl.glBufferSubData(gl.GL_ARRAY_BUFFER, 0, c_vertex_buffer_size, c_vertex_buffer)
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, None)
        gl.glEnableVertexAttribArray(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.uv_buffer)
        gl.glBufferSubData(gl.GL_ARRAY_BUFFER, 0, c_uv_buffer_size, c_uv_buffer)
        gl.glVertexAttribPointer(1, 2, gl.GL_FLOAT, gl.GL_FALSE, 0, None)

        gl.glBindVertexArray(0)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

        #========================================
        # Prepare Texture
        #========================================
        print("- Preparing textures.")
        # Load image
        image = cv2.imread(texture_filename)
        if image is None:
            print(f"[CV Error] Cannot open image: {texture_filename}")
            sys.exit()
        image = cv2.flip(image, 0)

        # Create texture
        self.texture = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture)

        # Generate texture
        gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)
        gl.glTexImage2D(
                gl.GL_TEXTURE_2D,  # target texture
                0,  # Mipmap Level
                gl.GL_RGBA,  # The number of color components in the texture
                image.shape[1],  # the width of texture
                image.shape[0],  # the height of texture
                0,  # border (this value must be 0)
                gl.GL_BGR,  # the format of the pixel data
                gl.GL_UNSIGNED_BYTE,  # the type of pixel data
                image)  # a pointer to the image

        # Set parameters
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_BORDER)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_BORDER)

        # Unbind
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

        #========================================
        # Prepare Camera Parameters
        #========================================
        print("- Setting camera parameters.")
        # Transform matrix
        trans = glm.vec3(0., 0., 50.)
        rot = glm.vec3(0.)
        transform_matrix = glm.mat4(1.)
        transform_matrix = glm.translate(transform_matrix, trans)
        transform_matrix = glm.rotate(transform_matrix, glm.radians(rot.x), glm.vec3(1., 0., 0.))
        transform_matrix = glm.rotate(transform_matrix, glm.radians(rot.y), glm.vec3(0., 1., 0.))
        transform_matrix = glm.rotate(transform_matrix, glm.radians(rot.z), glm.vec3(0., 0., 1.))

        self.default_camera_property = CameraProperty(
            transform_matrix = transform_matrix, 
            clipping_distance = glm.vec2(10., 1000.), 
            field_of_view = 60.)

        self.camera_property = self.default_camera_property.clone()

        #========================================
        # Prepare Shader Programs
        #========================================
        print("- Preparing shaders.")
        is_loaded: bool = False

        vert_shader = gl.glCreateShader(gl.GL_VERTEX_SHADER)
        is_loaded = Viewer.load_shader(vert_shader, f"{os.path.dirname(__file__)}/glsl/vertex.glsl")
        if not is_loaded: sys.exit()

        frag_shader = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)
        is_loaded = Viewer.load_shader(frag_shader, f"{os.path.dirname(__file__)}/glsl/fragment.glsl")
        if not is_loaded: sys.exit()

        # Create shader program
        self.shader_program = gl.glCreateProgram()

        # Bind shader objects
        gl.glAttachShader(self.shader_program, vert_shader)
        gl.glAttachShader(self.shader_program, frag_shader)
        gl.glDeleteShader(vert_shader)
        gl.glDeleteShader(frag_shader)

        # Link shader program
        gl.glLinkProgram(self.shader_program)
        result = gl.glGetProgramiv(self.shader_program, gl.GL_LINK_STATUS)
        if result != gl.GL_TRUE:
            print(f"[GLFW Error] {gl.glGetShaderInfoLog(shader_id)}")
            sys.exit()

        # Specify uniform variables
        gl.glUseProgram(self.shader_program)
        gl.glUniform1i(gl.glGetUniformLocation(self.shader_program, "sampler"), 0)

        #========================================
        # Prepare Other Instance Variables
        #========================================
        # Cursor status
        self.previous_cursor_status = CursorStatus(
                button = {
                    glfw.MOUSE_BUTTON_LEFT: False, 
                    glfw.MOUSE_BUTTON_RIGHT: False}, 
                position = glm.vec3(0.))

        print("Initialization done. ")
        Viewer.help()

    def update(self) -> bool:
        """
        @fn update()
        @brief Update the frame. 
        @return Whether the main loop continues. 
        """
        #========================================
        # Mouse and Keyboard response
        #========================================
        # Exit
        if glfw.get_key(self.window, glfw.KEY_ESCAPE) == glfw.PRESS:
            return False

        # Camera motion (keyboard)
        if glfw.get_key(self.window, glfw.KEY_SPACE) == glfw.PRESS:
            self.camera_property = self.default_camera_property.clone()
        else:
            trans = glm.vec3(0.)
            rot = glm.vec3(0.)
            trans_delta = 0.05
            rot_delta = 0.05
            if glfw.get_key(self.window, glfw.KEY_W) == glfw.PRESS:
                if glfw.get_key(self.window, glfw.KEY_LEFT_SHIFT) != glfw.PRESS:
                    trans.z += trans_delta
                else:
                    trans.y += trans_delta
            if glfw.get_key(self.window, glfw.KEY_S) == glfw.PRESS:
                if glfw.get_key(self.window, glfw.KEY_LEFT_SHIFT) != glfw.PRESS:
                    trans.z -= trans_delta
                else:
                    trans.y -= trans_delta
            if glfw.get_key(self.window, glfw.KEY_D) == glfw.PRESS:
                trans.x += trans_delta
            if glfw.get_key(self.window, glfw.KEY_A) == glfw.PRESS:
                trans.x -= trans_delta
            if glfw.get_key(self.window, glfw.KEY_UP) == glfw.PRESS:
                rot.x += rot_delta
            if glfw.get_key(self.window, glfw.KEY_DOWN) == glfw.PRESS:
                rot.x -= rot_delta
            if glfw.get_key(self.window, glfw.KEY_LEFT) == glfw.PRESS:
                rot.y += rot_delta
            if glfw.get_key(self.window, glfw.KEY_RIGHT) == glfw.PRESS:
                rot.y -= rot_delta

            tmat = glm.mat4(1.)
            tmat = glm.translate(tmat, -trans)
            tmat = glm.rotate(tmat, glm.radians(rot.x), glm.vec3(1., 0., 0.))
            tmat = glm.rotate(tmat, glm.radians(rot.y), glm.vec3(0., 1., 0.))
            tmat = glm.rotate(tmat, glm.radians(rot.z), glm.vec3(0., 0., 1.))
            self.camera_property.transform_matrix = tmat * self.camera_property.transform_matrix

        if glfw.get_key(self.window, glfw.KEY_R) == glfw.PRESS:
            tmat = glm.rotate(tmat, glm.radians(0.032), glm.vec3(0., 0., 1.))
            self.camera_property.transform_matrix = self.camera_property.transform_matrix * tmat


        # Camera motion (mouse)
        current_cursor_status = CursorStatus(
                button = {
                    glfw.MOUSE_BUTTON_LEFT: False, 
                    glfw.MOUSE_BUTTON_RIGHT: False}, 
                position = None)

        # Acquire current cursor status
        if glfw.get_mouse_button(self.window, glfw.MOUSE_BUTTON_LEFT) == glfw.PRESS:
            current_cursor_status.button[glfw.MOUSE_BUTTON_LEFT] = True
        if glfw.get_mouse_button(self.window, glfw.MOUSE_BUTTON_RIGHT) == glfw.PRESS:
            current_cursor_status.button[glfw.MOUSE_BUTTON_RIGHT] = True
        current_cursor_status.position = glm.vec2(glfw.get_cursor_pos(self.window))

        # Compare current status with previous one
        if current_cursor_status.button[glfw.MOUSE_BUTTON_LEFT]\
                and self.previous_cursor_status.button[glfw.MOUSE_BUTTON_LEFT]\
                and not current_cursor_status.button[glfw.MOUSE_BUTTON_RIGHT]\
                and not self.previous_cursor_status.button[glfw.MOUSE_BUTTON_RIGHT]:
                    displ = current_cursor_status.position - self.previous_cursor_status.position
                    displ *= 0.01  # scaling
                    displ = glm.vec3(displ.x, -displ.y, 0.)  # 2D -> 3D
                    tmat = glm.translate(glm.mat4(1.),  displ)
                    self.camera_property.transform_matrix = tmat * self.camera_property.transform_matrix

        elif current_cursor_status.button[glfw.MOUSE_BUTTON_RIGHT]\
                and self.previous_cursor_status.button[glfw.MOUSE_BUTTON_RIGHT]\
                and not current_cursor_status.button[glfw.MOUSE_BUTTON_LEFT]\
                and not self.previous_cursor_status.button[glfw.MOUSE_BUTTON_LEFT]:
                    displ = current_cursor_status.position - self.previous_cursor_status.position
                    displ *= -0.1  # scaling
                    displ = glm.vec3(displ.y, displ.x, 0.)  # 2D -> 3D
                    if glm.length(displ) != 0:
                        tmat = glm.rotate(glm.mat4(1.), glm.radians(glm.length(displ)),  glm.normalize(displ))
                        self.camera_property.transform_matrix = self.camera_property.transform_matrix * tmat

        self.previous_cursor_status = current_cursor_status

        #========================================
        # Update the camera matrix
        #========================================
        self.update_camera_matrix()

        #========================================
        # Draw new buffer
        #========================================
        # Initialize
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        #gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE);

        # Bind program
        gl.glUseProgram(self.shader_program)

        # Draw model
        if len(self.model_indices) // 3 > 0:
            # Bind buffer
            gl.glBindVertexArray(self.va_object)
            gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.index_buffer)

            # Bind buffer
            gl.glActiveTexture(gl.GL_TEXTURE0)
            gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture)

            # Draw
            #gl.glDrawArrays(gl.GL_TRIANGLES, 0, len(self.model_vertices) // 3)
            gl.glDrawElements(gl.GL_TRIANGLES, len(self.model_indices), 
                    gl.GL_UNSIGNED_INT, None)

            # Unbind
            gl.glBindVertexArray(0)
            gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

        # Update
        glfw.swap_buffers(self.window)
        glfw.poll_events()

        return glfw.window_should_close(self.window) != gl.GL_TRUE
        
