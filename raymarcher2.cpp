#include <math.h>
#include <unistd.h>
#include <time.h>

double t = 0.0;
#define WIDTH 80
#define HEIGHT 40
static char framebuffer[HEIGHT * WIDTH];

const int npixels = 7;
const char *pixels = " .:+|0#";


struct vec3 {
    float x;
    float y;
    float z;

    float length() {
        return sqrt(x*x + y*y + z*z);
    }

    void normalize() {
        float l = length();
        x = x / l; y = y / l; z = z / l;
    }

    struct vec3 operator*(float fac) {
        struct vec3 r;
        r.x = x * fac; r.y = y * fac; r.z = z * fac;
        return r;
    }

    struct vec3 operator+(struct vec3 other) {
        struct vec3 r;
        r.x = x +other.x; r.y = y +other.y; r.z = z + other.z;
        return r;
    }
    struct vec3 operator-(struct vec3 other) {
        struct vec3 r;
        r.x = x - other.x; r.y = y - other.y; r.z = z - other.z;
        return r;
    }

};

void raymarch();
float sdf(struct vec3);
char shade(struct vec3);


void raymarch() {
    for (int y = 0; y < HEIGHT; y++) {
        for (int x = 0; x < WIDTH; x++) {
            struct vec3 pos = {0.0, 0.0, -3.0};
            struct vec3 target = {
				x   / (float) WIDTH - 0.5f,
				(y / (float) HEIGHT - 0.5f) * (HEIGHT / (float) WIDTH) * 1.5f,
            		-1.5f
            	};

            struct vec3 ray = target - pos;
            ray.normalize();
            char pxl = pixels[0];
            float dist;
            float max = 9999.0f;
            for (int i = 0; i < 15000; i++) {
                if (fabs(pos.x) > max
                		|| fabs(pos.y) > max
                		|| fabs(pos.z) > max)
                	break;

                dist = sdf(pos);
                if (dist < 1e-6) {
                    pxl = shade(pos);
                    break;
                }

                pos = pos + ray * dist;
            } // end for (i)

            framebuffer[y * WIDTH + x] = pxl;
        } // end for(x)
    } // end for(y)
} // end raymarch()

float sdf(struct vec3 pos) {
	struct vec3 center = {0.0, 0.0, 0.0};
	
	return (pos - center).length() - 0.2;
}

char shade(struct vec3 pos) {
    struct vec3 L = {
    		50.0 * sin(t),
    		20.0,
    		50.0 * cos(t)
    };
    L.normalize();
    
    float dt = 1e-6;
	float current_val = sdf(pos);
	
	struct vec3 x = {pos.x + dt, pos.y, pos.z};
	float dx = sdf(x) - current_val;
	
	struct vec3 y = {pos.x, pos.y + dt, pos.z};
	float dy = sdf(y) - current_val;
	
	struct vec3 z = {pos.x, pos.y, pos.z + dt};
	float dz = sdf(z) - current_val;

	struct vec3 N; // N for normal
	N.x = (dx - pos.x) / dt;
	N.y = (dy - pos.y) / dt;
	N.z = (dz - pos.z) / dt;

    if (N.length() < 1e-9) {
        return pixels[0];
    }
	
	N.normalize();

	float diffuse = L.x * N.x + L.y * N.y + L.z * N.z;
	diffuse = (diffuse + 1.0) / 2.0 * npixels;
    return pixels[(int) floor(diffuse) % npixels];
}

// Terminal clear sequence
const char *cls_seq = "\e[1;1H\e[2J";

void cls() {
    write(0, cls_seq, 10);
}

void printfb() {
    char *fb = framebuffer;
    char nl = '\n';
    cls();
    for (int y = 0; y < HEIGHT; y++) {
        write(1, fb, WIDTH);
        write(1, &nl, 1);
        fb += WIDTH;

    }
}

int main() {
    for (int i = 0; i < WIDTH * HEIGHT; i++)
        framebuffer[i] = ' ';

    while(true) {
        double last_frame = t;
        raymarch();
        printfb();
        do {
            struct timespec time;
            clock_gettime(CLOCK_REALTIME, &time);
            t = time.tv_sec + time.tv_nsec * 1e-9;
        } while ((t - last_frame) < 1.0 / 60.0);
    }
}
