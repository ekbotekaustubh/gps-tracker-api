#include <GL/glew.h>
#include <GLFW/glfw3.h>
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
#include <glm/gtc/type_ptr.hpp>
#include <iostream>
#include <vector>
#include <string>

// Shader sources (same as before, included here for completeness)
const char* shader1_vs = R"(
#version 400 core
layout(location = 0) in vec2 vs_Position;
layout(location = 1) in vec2 vs_TexCoord;
out vec2 fs_TexCoord;
void main() {
    gl_Position = vec4(vs_Position, 0.0, 1.0);
    fs_TexCoord = vs_TexCoord;
}
)";

const char* shader1_fs = R"(
#version 400 core
uniform sampler2D spectrum_1_2_Sampler;
uniform sampler2D spectrum_3_4_Sampler;
uniform float FFT_SIZE;
uniform vec4 INVERSE_GRID_SIZES;
uniform float t;
layout(location = 0) out vec4 buffer0;
layout(location = 1) out vec4 buffer1;
layout(location = 2) out vec4 buffer2;
layout(location = 3) out vec4 buffer3;
layout(location = 4) out vec4 buffer4;
in vec2 fs_TexCoord;
vec2 getSpectrum(float k, vec2 s0, vec2 s0c) {
    float w = sqrt(9.81 * k * (1.0 + k * k / (370.0 * 370.0)));
    float c = cos(w * t);
    float s = sin(w * t);
    return vec2((s0.x + s0c.x) * c - (s0.y + s0c.y) * s, (s0.x - s0c.x) * s + (s0.y - s0c.y) * c);
}
vec2 i(vec2 z) {
    return vec2(-z.y, z.x);
}
void main() {
    vec2 st = floor(fs_TexCoord * FFT_SIZE) / FFT_SIZE;
    float x = fs_TexCoord.x > 0.5 ? st.x - 1.0 : st.x;
    float y = fs_TexCoord.y > 0.5 ? st.y - 1.0 : st.y;
    vec4 s12 = textureLod(spectrum_1_2_Sampler, fs_TexCoord, 0.0);
    vec4 s34 = textureLod(spectrum_3_4_Sampler, fs_TexCoord, 0.0);
    vec4 s12c = textureLod(spectrum_1_2_Sampler, vec2(1.0 + 0.5 / FFT_SIZE) - st, 0.0);
    vec4 s34c = textureLod(spectrum_3_4_Sampler, vec2(1.0 + 0.5 / FFT_SIZE) - st, 0.0);
    vec2 k1 = vec2(x, y) * INVERSE_GRID_SIZES.x;
    vec2 k2 = vec2(x, y) * INVERSE_GRID_SIZES.y;
    vec2 k3 = vec2(x, y) * INVERSE_GRID_SIZES.z;
    vec2 k4 = vec2(x, y) * INVERSE_GRID_SIZES.w;
    float K1 = length(k1);
    float K2 = length(k2);
    float K3 = length(k3);
    float K4 = length(k4);
    float IK1 = K1 == 0.0 ? 0.0 : 1.0 / K1;
    float IK2 = K2 == 0.0 ? 0.0 : 1.0 / K2;
    float IK3 = K3 == 0.0 ? 0.0 : 1.0 / K3;
    float IK4 = K4 == 0.0 ? 0.0 : 1.0 / K4;
    vec2 h1 = getSpectrum(K1, s12.xy, s12c.xy);
    vec2 h2 = getSpectrum(K2, s12.zw, s12c.zw);
    vec2 h3 = getSpectrum(K3, s34.xy, s34c.xy);
    vec2 h4 = getSpectrum(K4, s34.zw, s34c.zw);
    buffer0 = vec4(h1 + i(h2), h3 + i(h4));
    buffer1 = vec4(i(k1.x * h1) - k1.y * h1, i(k2.x * h2) - k2.y * h2);
    buffer2 = vec4(i(k3.x * h3) - k3.y * h3, i(k4.x * h4) - k4.y * h4);
    buffer3 = buffer1 * vec4(IK1, IK1, IK2, IK2);
    buffer4 = buffer2 * vec4(IK3, IK3, IK4, IK4);
}
)";

const char* shader2_vs = R"(
#version 400 core
layout(location = 0) in vec2 vs_Position;
layout(location = 1) in vec2 vs_TexCoord;
out vec2 fs_TexCoord;
void main() {
    gl_Position = vec4(vs_Position, 0.0, 1.0);
    fs_TexCoord = vs_TexCoord;
}
)";

const char* shader2_fs = R"(
#version 400 core
#define M_PI 3.14159265
uniform sampler2D spectrum_1_2_Sampler;
uniform sampler2D spectrum_3_4_Sampler;
uniform int FFT_SIZE;
uniform vec4 GRID_SIZES;
uniform float N_SLOPE_VARIANCE;
uniform float slopeVarianceDelta;
uniform float c;
layout(location = 0) out float frag;
in vec2 fs_TexCoord;
float getSlopeVariance(vec2 k, float A, float B, float C, vec2 spectrumSample) {
    float w = 1.0 - exp(A * k.x * k.x + B * k.x * k.y + C * k.y * k.y);
    vec2 kw = k * w;
    return dot(kw, kw) * dot(spectrumSample, spectrumSample) * 2.0;
}
void main() {
    const float SCALE = 10.0;
    float a = floor(fs_TexCoord.x * N_SLOPE_VARIANCE);
    float b = floor(fs_TexCoord.y * N_SLOPE_VARIANCE);
    float A = pow(a / (N_SLOPE_VARIANCE - 1.0), 4.0) * SCALE;
    float C = pow(c / (N_SLOPE_VARIANCE - 1.0), 4.0) * SCALE;
    float B = (2.0 * b / (N_SLOPE_VARIANCE - 1.0) - 1.0) * sqrt(A * C);
    A = -0.5 * A;
    B = -B;
    C = -0.5 * C;
    float slopeVariance = slopeVarianceDelta;
    for (int y = 0; y < FFT_SIZE; ++y) {
        for (int x = 0; x < FFT_SIZE; ++x) {
            int i = x >= FFT_SIZE / 2 ? x - FFT_SIZE : x;
            int j = y >= FFT_SIZE / 2 ? y - FFT_SIZE : y;
            vec2 k = 2.0 * M_PI * vec2(i, j);
            vec4 spectrum12 = texture(spectrum_1_2_Sampler, vec2(float(x) + 0.5, float(y) + 0.5) / float(FFT_SIZE));
            vec4 spectrum34 = texture(spectrum_3_4_Sampler, vec2(float(x) + 0.5, float(y) + 0.5) / float(FFT_SIZE));
            slopeVariance += getSlopeVariance(k / GRID_SIZES.x, A, B, C, spectrum12.xy);
            slopeVariance += getSlopeVariance(k / GRID_SIZES.y, A, B, C, spectrum12.zw);
            slopeVariance += getSlopeVariance(k / GRID_SIZES.z, A, B, C, spectrum34.xy);
            slopeVariance += getSlopeVariance(k / GRID_SIZES.w, A, B, C, spectrum34.zw);
        }
    }
    frag = slopeVariance;
}
)";

const char* shader3_vs = R"(
#version 400 core
layout(location = 0) in vec2 vs_Position;
layout(location = 1) in vec2 vs_TexCoord;
out vec2 gs_TexCoord;
void main() {
    gl_Position = vec4(vs_Position, 0.0, 1.0);
    gs_TexCoord = vs_TexCoord;
}
)";

const char* shader3_gs = R"(
#version 400 core
layout(triangles) in;
layout(triangle_strip, max_vertices = 15) out;
in vec2 gs_TexCoord[];
out vec2 fs_TexCoord;
void main() {
    for (int i = 0; i < 5; ++i) {
        gl_Layer = i;
        gl_PrimitiveID = i;
        gl_Position = gl_in[0].gl_Position;	
        fs_TexCoord = gs_TexCoord[0];
        EmitVertex();
        gl_Position = gl_in[1].gl_Position;
        fs_TexCoord = gs_TexCoord[1];
        EmitVertex();
        gl_Position = gl_in[2].gl_Position;
        fs_TexCoord = gs_TexCoord[2];
        EmitVertex();
        EndPrimitive();
    }
}
)";

const char* shader3_fs = R"(
#version 400 core
uniform sampler2D butterflySampler;
uniform sampler2DArray imgSampler;
uniform float pass;
layout(location = 0) out vec4 frag;
in vec2 fs_TexCoord;
vec4 fft2(int layer, vec2 i, vec2 w) {
    vec4 input1 = texture(imgSampler, vec3(i.x, fs_TexCoord.y, layer), 0.0);
    vec4 input2 = texture(imgSampler, vec3(i.y, fs_TexCoord.y, layer), 0.0);
    float res1x = w.x * input2.x - w.y * input2.y;
    float res1y = w.y * input2.x + w.x * input2.y;
    float res2x = w.x * input2.z - w.y * input2.w;
    float res2y = w.y * input2.z + w.x * input2.w;
    return input1 + vec4(res1x, res1y, res2x, res2y);
}
void main() {
    vec4 data = texture(butterflySampler, vec2(fs_TexCoord.x, pass), 0.0);
    vec2 i = data.xy;
    vec2 w = data.zw;
    frag = fft2(gl_PrimitiveID, i, w);
}
)";

const char* shader4_vs = R"(
#version 400 core
layout(location = 0) in vec2 vs_Position;
layout(location = 1) in vec2 vs_TexCoord;
out vec2 gs_TexCoord;
void main() {
    gl_Position = vec4(vs_Position, 0.0, 1.0);
    gs_TexCoord = vs_TexCoord;
}
)";

const char* shader4_gs = R"(
#version 400 core
layout(triangles) in;
layout(triangle_strip, max_vertices = 15) out;
in vec2 gs_TexCoord[];
out vec2 fs_TexCoord;
void main() {
    for (int i = 0; i < 5; ++i) {
        gl_Layer = i;
        gl_PrimitiveID = i;
        gl_Position = gl_in[0].gl_Position;	
        fs_TexCoord = gs_TexCoord[0];
        EmitVertex();
        gl_Position = gl_in[1].gl_Position;
        fs_TexCoord = gs_TexCoord[1];
        EmitVertex();
        gl_Position = gl_in[2].gl_Position;
        fs_TexCoord = gs_TexCoord[2];
        EmitVertex();
        EndPrimitive();
    }
}
)";

const char* shader4_fs = R"(
#version 400 core
uniform sampler2D butterflySampler;
uniform sampler2DArray imgSampler;
uniform float pass;
layout(location = 0) out vec4 frag;
in vec2 fs_TexCoord;
vec4 fft2(int layer, vec2 i, vec2 w) {
    vec4 input1 = texture(imgSampler, vec3(fs_TexCoord.x, i.x, layer), 0.0);
    vec4 input2 = texture(imgSampler, vec3(fs_TexCoord.x, i.y, layer), 0.0);
    float res1x = w.x * input2.x - w.y * input2.y;
    float res1y = w.y * input2.x + w.x * input2.y;
    float res2x = w.x * input2.z - w.y * input2.w;
    float res2y = w.y * input2.z + w.x * input2.w;
    return input1 + vec4(res1x, res1y, res2x, res2y);
}
void main() {
    vec4 data = texture(butterflySampler, vec2(fs_TexCoord.y, pass), 0.0);
    vec2 i = data.xy;
    vec2 w = data.zw;
    frag = fft2(gl_PrimitiveID, i, w);
}
)";

const char* shader5_vs = R"(
#version 400 core
layout(location = 0) in vec4 vs_Position;
out vec3 fs_Position;
out vec2 fs_TexCoord;
out float fs_Flogz;
uniform mat4 _Ocean_CameraToScreen;
uniform mat4 _Ocean_ScreenToCamera;
uniform mat4 _Ocean_CameraToOcean;
uniform mat3 _Ocean_OceanToCamera;
uniform mat4 _Ocean_OceanToWorld;
uniform vec3 _Ocean_Horizon1;
uniform vec3 _Ocean_Horizon2;
uniform vec3 _Ocean_CameraPos;
uniform vec2 _Ocean_ScreenGridSize;
uniform float _Ocean_Radius;
uniform sampler2DArray fftWavesSampler;
uniform vec4 GRID_SIZES;
vec2 oceanPos(vec3 vertex, out float t, out vec3 cameraDir, out vec3 oceanDir) {
    float horizon = _Ocean_Horizon1.x + _Ocean_Horizon1.y * vertex.x - sqrt(_Ocean_Horizon2.x + (_Ocean_Horizon2.y + _Ocean_Horizon2.z * vertex.x) * vertex.x);
    cameraDir = normalize((_Ocean_ScreenToCamera * vec4(vertex.x, min(vertex.y, horizon), 0.0, 1.0)).xyz);
    oceanDir = (_Ocean_CameraToOcean * vec4(cameraDir, 0.0)).xyz;
    float cz = _Ocean_CameraPos.z;
    float dz = oceanDir.z;
    float b = dz * (cz + _Ocean_Radius);
    float c = cz * (cz + 2.0 * _Ocean_Radius);
    float tSphere = -b - sqrt(max(b * b - c, 0.0));
    float tApprox = -cz / dz * (1.0 + cz / (2.0 * _Ocean_Radius) * (1.0 - dz * dz));
    t = abs((tApprox - tSphere) * dz) < 1.0 ? tApprox : tSphere;
    return _Ocean_CameraPos.xy + t * oceanDir.xy;
}
vec2 oceanPos(vec3 vertex) {
    float t;
    vec3 cameraDir;
    vec3 oceanDir;
    return oceanPos(vertex, t, cameraDir, oceanDir);
}
void main() {
    float t;
    vec3 cameraDir;
    vec3 oceanDir;
    vec3 vertex = vs_Position.xyz;
    vertex.xy *= 1.25f;
    vec2 u = oceanPos(vertex, t, cameraDir, oceanDir);
    vec2 dux = oceanPos(vertex + vec3(_Ocean_ScreenGridSize.x, 0.0, 0.0)) - u;
    vec2 duy = oceanPos(vertex + vec3(0.0, _Ocean_ScreenGridSize.y, 0.0)) - u;
    vec3 dP = vec3(0.0, 0.0, 0.0);
    if (duy.x != 0.0 || duy.y != 0.0) {
        dP.z += textureGrad(fftWavesSampler, vec3(u / GRID_SIZES.x, 0.0), dux / GRID_SIZES.x, duy / GRID_SIZES.x).x;
        dP.z += textureGrad(fftWavesSampler, vec3(u / GRID_SIZES.y, 0.0), dux / GRID_SIZES.y, duy / GRID_SIZES.y).y;
        dP.z += textureGrad(fftWavesSampler, vec3(u / GRID_SIZES.z, 0.0), dux / GRID_SIZES.z, duy / GRID_SIZES.z).z;
        dP.z += textureGrad(fftWavesSampler, vec3(u / GRID_SIZES.w, 0.0), dux / GRID_SIZES.w, duy / GRID_SIZES.w).w;
        dP.xy += 2.5 * textureGrad(fftWavesSampler, vec3(u / GRID_SIZES.x, 3.0), dux / GRID_SIZES.x, duy / GRID_SIZES.x).xy;
        dP.xy += 2.5 * textureGrad(fftWavesSampler, vec3(u / GRID_SIZES.y, 3.0), dux / GRID_SIZES.y, duy / GRID_SIZES.y).zw;
        dP.xy += 2.5 * textureGrad(fftWavesSampler, vec3(u / GRID_SIZES.z, 4.0), dux / GRID_SIZES.z, duy / GRID_SIZES.z).xy;
        dP.xy += 2.5 * textureGrad(fftWavesSampler, vec3(u / GRID_SIZES.w, 4.0), dux / GRID_SIZES.w, duy / GRID_SIZES.w).zw;
    }
    gl_Position = _Ocean_CameraToScreen * vec4(t * cameraDir + _Ocean_OceanToCamera * dP, 1.0);   
    fs_Position = vec3(0.0, 0.0, _Ocean_CameraPos.z) + t * oceanDir + dP;
    fs_TexCoord = u;
}
)";

const char* shader5_fs = R"(
#version 400 core
uniform sampler2DArray fftWavesSampler;
uniform vec4 GRID_SIZES;
uniform sampler3D slopeVarianceSampler;
uniform mat4 _Ocean_OceanToWorld;
uniform vec3 _Ocean_CameraPos;
uniform float _Ocean_Radius;
uniform float u_DepthSplit;
uniform vec3 u_SunDir;
uniform samplerCube s_Cubemap;
layout(location = 0) out vec4 diffuse;
layout(location = 1) out vec4 geometric;
in vec3 fs_Position;
in vec2 fs_TexCoord;
void main() {
    vec2 slopes = texture(fftWavesSampler, vec3(fs_TexCoord / GRID_SIZES.x, 1.0)).xy;
    slopes += texture(fftWavesSampler, vec3(fs_TexCoord / GRID_SIZES.y, 1.0)).zw;
    slopes += texture(fftWavesSampler, vec3(fs_TexCoord / GRID_SIZES.z, 2.0)).xy;
    slopes += texture(fftWavesSampler, vec3(fs_TexCoord / GRID_SIZES.w, 2.0)).zw;
    slopes -= fs_Position.xy / (_Ocean_Radius + fs_Position.z);
    vec3 V = normalize(vec3(0, 0, _Ocean_CameraPos.z) - fs_Position);
    vec3 N = normalize(vec3(-slopes.x, -slopes.y, 1.0));
    if (dot(V, N) < 0.0) {
        N = reflect(N, V);
    }
    float Jxx = dFdx(fs_TexCoord.x);
    float Jxy = dFdy(fs_TexCoord.x);
    float Jyx = dFdx(fs_TexCoord.y);
    float Jyy = dFdy(fs_TexCoord.y);
    float A = Jxx * Jxx + Jyx * Jyx;
    float B = Jxx * Jxy + Jyx * Jyy;
    float C = Jxy * Jxy + Jyy * Jyy;
    const float SCALE = 10.0;
    float ua = pow(A / SCALE, 0.25);
    float ub = 0.5 + 0.5 * B / sqrt(A * C);
    float uc = pow(C / SCALE, 0.25);
    float roughness = max(texture(slopeVarianceSampler, vec3(ua, ub, uc)).x, 2e-5);
    vec3 fn = normalize(mat3(_Ocean_OceanToWorld) * N);
    vec3 color = vec3(0.039f, 0.156f, 0.47f) * 0.02;
    if (gl_FragCoord.z >= u_DepthSplit) {
        vec3 p = (_Ocean_OceanToWorld * vec4(fs_Position, 1.0)).xyz;
        vec3 I = p - u_CameraPos;
        vec3 R = reflect(I, fn);      
        vec3 reflect = texture(s_Cubemap, R).rgb;       
        color = mix(color, reflect, roughness * 1000.0);    
        float shadow = 1.0; // Placeholder, implement shadow calculation if needed
        color = color * max(dot(u_SunDir, fn), 0.0) * shadow; // Simple lighting
    }
    diffuse = vec4(color, 1);
    geometric = vec4(fn * 0.5 + 0.5, roughness * 1000.0);
}
)";

// Compile shader
GLuint compileShader(GLenum type, const char* source) {
    GLuint shader = glCreateShader(type);
    glShaderSource(shader, 1, &source, nullptr);
    glCompileShader(shader);
    GLint success;
    glGetShaderiv(shader, GL_COMPILE_STATUS, &success);
    if (!success) {
        char infoLog[512];
        glGetShaderInfoLog(shader, 512, nullptr, infoLog);
        std::cerr << "Shader compilation failed: " << infoLog << std::endl;
    }
    return shader;
}

// Create shader program
GLuint createProgram(const char* vsSource, const char* fsSource, const char* gsSource = nullptr) {
    GLuint vs = compileShader(GL_VERTEX_SHADER, vsSource);
    GLuint fs = compileShader(GL_FRAGMENT_SHADER, fsSource);
    GLuint gs = gsSource ? compileShader(GL_GEOMETRY_SHADER, gsSource) : 0;

    GLuint program = glCreateProgram();
    glAttachShader(program, vs);
    glAttachShader(program, fs);
    if (gs) glAttachShader(program, gs);
    glLinkProgram(program);

    GLint success;
    glGetProgramiv(program, GL_LINK_STATUS, &success);
    if (!success) {
        char infoLog[512];
        glGetProgramInfoLog(program, 512, nullptr, infoLog);
        std::cerr << "Program linking failed: " << infoLog << std::endl;
    }

    glDeleteShader(vs);
    glDeleteShader(fs);
    if (gs) glDeleteShader(gs);

    return program;
}

int main() {
    // Initialize GLFW
    if (!glfwInit()) {
        std::cerr << "Failed to initialize GLFW" << std::endl;
        return -1;
    }

    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 4);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 0);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);

    GLFWwindow* window = glfwCreateWindow(800, 600, "Ocean Rendering", nullptr, nullptr);
    if (!window) {
        std::cerr << "Failed to create GLFW window" << std::endl;
        glfwTerminate();
        return -1;
    }

    glfwMakeContextCurrent(window);

    // Initialize GLEW
    if (glewInit() != GLEW_OK) {
        std::cerr << "Failed to initialize GLEW" << std::endl;
        glfwTerminate();
        return -1;
    }

    // Create shader programs
    GLuint program1 = createProgram(shader1_vs, shader1_fs);
    GLuint program2 = createProgram(shader2_vs, shader2_fs);
    GLuint program3 = createProgram(shader3_vs, shader3_fs, shader3_gs);
    GLuint program4 = createProgram(shader4_vs, shader4_fs, shader4_gs);
    GLuint program5 = createProgram(shader5_vs, shader5_fs);

    // Quad vertices
    float vertices[] = {
        -1.0f, -1.0f, 0.0f, 0.0f,
         1.0f, -1.0f, 1.0f, 0.0f,
        -1.0f,  1.0f, 0.0f, 1.0f,
         1.0f,  1.0f, 1.0f, 1.0f
    };

    GLuint vao, vbo;
    glGenVertexArrays(1, &vao);
    glGenBuffers(1, &vbo);

    glBindVertexArray(vao);
    glBindBuffer(GL_ARRAY_BUFFER, vbo);
    glBufferData(GL_ARRAY_BUFFER, sizeof(vertices), vertices, GL_STATIC_DRAW);

    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 4 * sizeof(float), (void*)0);
    glEnableVertexAttribArray(0);
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 4 * sizeof(float), (void*)(2 * sizeof(float)));
    glEnableVertexAttribArray(1);

    // Placeholder textures with dummy data
    const int FFT_SIZE = 256;
    GLuint spectrum12, spectrum34, butterfly, img, fftWaves, slopeVariance, cubemap;
    glGenTextures(1, &spectrum12);
    glGenTextures(1, &spectrum34);
    glGenTextures(1, &butterfly);
    glGenTextures(1, &img);
    glGenTextures(1, &fftWaves);
    glGenTextures(1, &slopeVariance);
    glGenTextures(1, &cubemap);

    // Dummy data for textures
    std::vector<float> dummyData(FFT_SIZE * FFT_SIZE * 4, 1.0f); // White noise
    std::vector<float> imgData(FFT_SIZE * FFT_SIZE * 5 * 4, 0.5f); // Half-gray
    std::vector<float> slopeData(64 * 64 * 64, 0.01f); // Small variance

    glBindTexture(GL_TEXTURE_2D, spectrum12);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA32F, FFT_SIZE, FFT_SIZE, 0, GL_RGBA, GL_FLOAT, nullptr);
    glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, FFT_SIZE, FFT_SIZE, GL_RGBA, GL_FLOAT, dummyData.data());
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);

    glBindTexture(GL_TEXTURE_2D, spectrum34);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA32F, FFT_SIZE, FFT_SIZE, 0, GL_RGBA, GL_FLOAT, nullptr);
    glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, FFT_SIZE, FFT_SIZE, GL_RGBA, GL_FLOAT, dummyData.data());
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);

    glBindTexture(GL_TEXTURE_2D, butterfly);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA32F, FFT_SIZE, FFT_SIZE, 0, GL_RGBA, GL_FLOAT, nullptr);
    glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, FFT_SIZE, FFT_SIZE, GL_RGBA, GL_FLOAT, dummyData.data());
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);

    glBindTexture(GL_TEXTURE_2D_ARRAY, img);
    glTexImage3D(GL_TEXTURE_2D_ARRAY, 0, GL_RGBA32F, FFT_SIZE, FFT_SIZE, 5, 0, GL_RGBA, GL_FLOAT, nullptr);
    glTexSubImage3D(GL_TEXTURE_2D_ARRAY, 0, 0, 0, 0, FFT_SIZE, FFT_SIZE, 5, GL_RGBA, GL_FLOAT, imgData.data());
    glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_MAG_FILTER, GL_LINEAR);

    glBindTexture(GL_TEXTURE_2D_ARRAY, fftWaves);
    glTexImage3D(GL_TEXTURE_2D_ARRAY, 0, GL_RGBA32F, FFT_SIZE, FFT_SIZE, 5, 0, GL_RGBA, GL_FLOAT, nullptr);
    glTexSubImage3D(GL_TEXTURE_2D_ARRAY, 0, 0, 0, 0, FFT_SIZE, FFT_SIZE, 5, GL_RGBA, GL_FLOAT, imgData.data());
    glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_MAG_FILTER, GL_LINEAR);

    glBindTexture(GL_TEXTURE_3D, slopeVariance);
    glTexImage3D(GL_TEXTURE_3D, 0, GL_R32F, 64, 64, 64, 0, GL_RED, GL_FLOAT, nullptr);
    glTexSubImage3D(GL_TEXTURE_3D, 0, 0, 0, 0, 64, 64, 64, GL_RED, GL_FLOAT, slopeData.data());
    glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);

    // Cubemap placeholder
    glBindTexture(GL_TEXTURE_CUBE_MAP, cubemap);
    for (int i = 0; i < 6; ++i) {
        glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, GL_RGB, 1, 1, 0, GL_RGB, GL_FLOAT, &glm::vec3(0.5f, 0.5f, 0.5f));
    }
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE);

    // Framebuffer for multiple render targets
    GLuint fbo;
    glGenFramebuffers(1, &fbo);
    glBindFramebuffer(GL_FRAMEBUFFER, fbo);

    GLuint colorBuffers[5];
    glGenTextures(5, colorBuffers);
    for (int i = 0; i < 5; ++i) {
        glBindTexture(GL_TEXTURE_2D, colorBuffers[i]);
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA32F, 800, 600, 0, GL_RGBA, GL_FLOAT, nullptr);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0 + i, GL_TEXTURE_2D, colorBuffers[i], 0);
    }

    GLenum drawBuffers[5] = { GL_COLOR_ATTACHMENT0, GL_COLOR_ATTACHMENT1, GL_COLOR_ATTACHMENT2, GL_COLOR_ATTACHMENT3, GL_COLOR_ATTACHMENT4 };
    glDrawBuffers(5, drawBuffers);

    if (glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE) {
        std::cerr << "Framebuffer is not complete!" << std::endl;
    }

    glBindFramebuffer(GL_FRAMEBUFFER, 0);

    // Camera setup
    glm::mat4 proj = glm::perspective(glm::radians(45.0f), 800.0f / 600.0f, 0.1f, 1000.0f);
    glm::mat4 view = glm::lookAt(glm::vec3(0, 0, 100), glm::vec3(0, 0, 0), glm::vec3(0, 1, 0));
    glm::mat4 oceanToWorld = glm::mat4(1.0f);
    glm::vec3 cameraPos(0, 0, 100);

    float time = 0.0f;

    // Main loop
    while (!glfwWindowShouldClose(window)) {
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
        glEnable(GL_DEPTH_TEST);

        // Update time
        time += 0.016f;

        // Shader 1 (Spectrum computation)
        glBindFramebuffer(GL_FRAMEBUFFER, fbo);
        glUseProgram(program1);
        glUniform1f(glGetUniformLocation(program1, "FFT_SIZE"), (float)FFT_SIZE);
        glUniform4f(glGetUniformLocation(program1, "INVERSE_GRID_SIZES"), 1.0f / 1000.0f, 1.0f / 500.0f, 1.0f / 250.0f, 1.0f / 125.0f);
        glUniform1f(glGetUniformLocation(program1, "t"), time);
        glActiveTexture(GL_TEXTURE0);
        glBindTexture(GL_TEXTURE_2D, spectrum12);
        glUniform1i(glGetUniformLocation(program1, "spectrum_1_2_Sampler"), 0);
        glActiveTexture(GL_TEXTURE1);
        glBindTexture(GL_TEXTURE_2D, spectrum34);
        glUniform1i(glGetUniformLocation(program1, "spectrum_3_4_Sampler"), 1);
        glBindVertexArray(vao);
        glDrawArrays(GL_TRIANGLE_STRIP, 0, 4);

        // Shader 2 (Slope variance)
        glBindFramebuffer(GL_FRAMEBUFFER, 0);
        glUseProgram(program2);
        glUniform1i(glGetUniformLocation(program2, "FFT_SIZE"), FFT_SIZE);
        glUniform4f(glGetUniformLocation(program2, "GRID_SIZES"), 1000.0f, 500.0f, 250.0f, 125.0f);
        glUniform1f(glGetUniformLocation(program2, "N_SLOPE_VARIANCE"), 64.0f);
        glUniform1f(glGetUniformLocation(program2, "slopeVarianceDelta"), 0.0f);
        glUniform1f(glGetUniformLocation(program2, "c"), 0.5f);
        glActiveTexture(GL_TEXTURE0);
        glBindTexture(GL_TEXTURE_2D, spectrum12);
        glUniform1i(glGetUniformLocation(program2, "spectrum_1_2_Sampler"), 0);
        glActiveTexture(GL_TEXTURE1);
        glBindTexture(GL_TEXTURE_2D, spectrum34);
        glUniform1i(glGetUniformLocation(program2, "spectrum_3_4_Sampler"), 1);
        glDrawArrays(GL_TRIANGLE_STRIP, 0, 4);

        // Shader 3 (FFT pass 1)
        glUseProgram(program3);
        glUniform1f(glGetUniformLocation(program3, "pass"), 0.0f);
        glActiveTexture(GL_TEXTURE0);
        glBindTexture(GL_TEXTURE_2D, butterfly);
        glUniform1i(glGetUniformLocation(program3, "butterflySampler"), 0);
        glActiveTexture(GL_TEXTURE1);
        glBindTexture(GL_TEXTURE_2D_ARRAY, img);
        glUniform1i(glGetUniformLocation(program3, "imgSampler"), 1);
        glBindFramebuffer(GL_FRAMEBUFFER, fbo);
        glDrawArrays(GL_TRIANGLE_STRIP, 0, 4);

        // Shader 4 (FFT pass 2)
        glUseProgram(program4);
        glUniform1f(glGetUniformLocation(program4, "pass"), 1.0f);
        glActiveTexture(GL_TEXTURE0);
        glBindTexture(GL_TEXTURE_2D, butterfly);
        glUniform1i(glGetUniformLocation(program4, "butterflySampler"), 0);
        glActiveTexture(GL_TEXTURE1);
        glBindTexture(GL_TEXTURE_2D_ARRAY, img);
        glUniform1i(glGetUniformLocation(program4, "imgSampler"), 1);
        glBindFramebuffer(GL_FRAMEBUFFER, fbo);
        glDrawArrays(GL_TRIANGLE_STRIP, 0, 4);

        // Shader 5 (Final ocean rendering)
        glBindFramebuffer(GL_FRAMEBUFFER, 0);
        glUseProgram(program5);
        glUniformMatrix4fv(glGetUniformLocation(program5, "_Ocean_CameraToScreen"), 1, GL_FALSE, glm::value_ptr(proj * view));
        glUniformMatrix4fv(glGetUniformLocation(program5, "_Ocean_ScreenToCamera"), 1, GL_FALSE, glm::value_ptr(glm::inverse(proj * view)));
        glUniformMatrix4fv(glGetUniformLocation(program5, "_Ocean_CameraToOcean"), 1, GL_FALSE, glm::value_ptr(glm::inverse(view)));
        glUniformMatrix3fv(glGetUniformLocation(program5, "_Ocean_OceanToCamera"), 1, GL_FALSE, glm::value_ptr(glm::mat3(view)));
        glUniformMatrix4fv(glGetUniformLocation(program5, "_Ocean_OceanToWorld"), 1, GL_FALSE, glm::value_ptr(oceanToWorld));
        glUniform3f(glGetUniformLocation(program5, "_Ocean_Horizon1"), 0.0f, 0.0f, 0.0f);
        glUniform3f(glGetUniformLocation(program5, "_Ocean_Horizon2"), 1.0f, 0.0f, 0.0f);
        glUniform3fv(glGetUniformLocation(program5, "_Ocean_CameraPos"), 1, glm::value_ptr(cameraPos));
        glUniform2f(glGetUniformLocation(program5, "_Ocean_ScreenGridSize"), 0.01f, 0.01f);
        glUniform1f(glGetUniformLocation(program5, "_Ocean_Radius"), 6360000.0f);
        glUniform4f(glGetUniformLocation(program5, "GRID_SIZES"), 1000.0f, 500.0f, 250.0f, 125.0f);
        glUniform1f(glGetUniformLocation(program5, "u_DepthSplit"), 0.99f);
        glUniform3f(glGetUniformLocation(program5, "u_SunDir"), 0.0f, 0.0f, -1.0f);
        glUniform3f(glGetUniformLocation(program5, "u_CameraPos"), 0.0f, 0.0f, 100.0f); // Match cameraPos
        glActiveTexture(GL_TEXTURE0);
        glBindTexture(GL_TEXTURE_2D_ARRAY, fftWaves);
        glUniform1i(glGetUniformLocation(program5, "fftWavesSampler"), 0);
        glActiveTexture(GL_TEXTURE1);
        glBindTexture(GL_TEXTURE_3D, slopeVariance);
        glUniform1i(glGetUniformLocation(program5, "slopeVarianceSampler"), 1);
        glActiveTexture(GL_TEXTURE2);
        glBindTexture(GL_TEXTURE_CUBE_MAP, cubemap);
        glUniform1i(glGetUniformLocation(program5, "s_Cubemap"), 2);
        glDrawArrays(GL_TRIANGLE_STRIP, 0, 4);

        glfwSwapBuffers(window);
        glfwPollEvents();
    }

    // Cleanup
    glDeleteVertexArrays(1, &vao);
    glDeleteBuffers(1, &vbo);
    glDeleteProgram(program1);
    glDeleteProgram(program2);
    glDeleteProgram(program3);
    glDeleteProgram(program4);
    glDeleteProgram(program5);
    glDeleteTextures(1, &spectrum12);
    glDeleteTextures(1, &spectrum34);
    glDeleteTextures(1, &butterfly);
    glDeleteTextures(1, &img);
    glDeleteTextures(1, &fftWaves);
    glDeleteTextures(1, &slopeVariance);
    glDeleteTextures(1, &cubemap);
    glDeleteFramebuffers(1, &fbo);
    glDeleteTextures(5, colorBuffers);

    glfwDestroyWindow(window);
    glfwTerminate();

    return 0;
}