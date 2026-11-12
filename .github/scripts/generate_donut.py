import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
WIDTH, HEIGHT = 78, 30
SCALE = 2
FRAME_COUNT = 60
CHARACTERS = ".,-~:;=!*#$@"
HERO_WIDTH = 1000
DONUT_WIDTH = 390
DONUT_OPACITY = 34
FONT_PATHS = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationMono-Regular.ttf",
)


def render_frame(frame_number, font):
    angle_a = frame_number * 2 * math.pi / FRAME_COUNT
    angle_b = frame_number * 4 * math.pi / FRAME_COUNT
    z_buffer = [0.0] * (WIDTH * HEIGHT)
    output = [" "] * (WIDTH * HEIGHT)

    for ii in range(0, 628, 3):
        i = ii / 100
        for jj in range(0, 628, 2):
            j = jj / 100
            sine_i, cosine_i = math.sin(i), math.cos(i)
            sine_j, cosine_j = math.sin(j), math.cos(j)
            sine_a, cosine_a = math.sin(angle_a), math.cos(angle_a)
            depth = 1 / (cosine_i * (cosine_j + 2) * sine_a + sine_j * cosine_a + 5)
            cosine_b, sine_b = math.cos(angle_b), math.sin(angle_b)
            tangent = cosine_i * (cosine_j + 2) * cosine_a - sine_j * sine_a
            x = int(WIDTH / 2 + 34 * depth * (sine_i * (cosine_j + 2) * cosine_b - tangent * sine_b))
            y = int(HEIGHT / 2 + 17 * depth * (sine_i * (cosine_j + 2) * sine_b + tangent * cosine_b))
            brightness = int(8 * ((sine_j * sine_a - cosine_i * cosine_j * cosine_a) * cosine_b - cosine_i * cosine_j * sine_a - sine_j * cosine_a - sine_i * cosine_j * sine_b))
            if 0 <= x < WIDTH and 0 <= y < HEIGHT and depth > z_buffer[x + WIDTH * y]:
                index = x + WIDTH * y
                z_buffer[index] = depth
                output[index] = CHARACTERS[max(0, min(len(CHARACTERS) - 1, brightness))]

    image = Image.new("RGBA", (WIDTH * 9 * SCALE, HEIGHT * 16 * SCALE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    for y in range(HEIGHT):
        for x in range(WIDTH):
            character = output[x + WIDTH * y]
            if character != " ":
                draw.text((x * 9 * SCALE, y * 16 * SCALE), character, font=font, fill=(255, 255, 255, 255))
    image.thumbnail((720, 330))
    return image


def main():
    font_path = next((path for path in FONT_PATHS if Path(path).exists()), None)
    font = ImageFont.truetype(font_path, 14 * SCALE) if font_path else ImageFont.load_default()
    banner_path = ROOT / "me.png"
    banner = Image.open(banner_path).convert("RGBA")
    hero_height = round(banner.height * HERO_WIDTH / banner.width)
    banner = banner.resize((HERO_WIDTH, hero_height), Image.Resampling.LANCZOS)

    frames = []
    for number in range(FRAME_COUNT):
        donut = render_frame(number, font)
        donut_height = round(donut.height * DONUT_WIDTH / donut.width)
        donut = donut.resize((DONUT_WIDTH, donut_height), Image.Resampling.LANCZOS)
        donut.putalpha(donut.getchannel("A").point(lambda alpha: alpha * DONUT_OPACITY // 255))

        frame = banner.copy()
        # Keep the animation behind the headline, away from the portrait and contact details.
        position = (HERO_WIDTH - DONUT_WIDTH - 65, 35)
        frame.alpha_composite(donut, position)
        frames.append(frame.convert("RGB").quantize(colors=128, method=Image.Quantize.MEDIANCUT))

    output_path = ROOT / "profile-banner.gif"
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=100,
        loop=0,
        optimize=True,
        disposal=1,
    )
    print(f"Generated animated hero banner at {output_path}")


if __name__ == "__main__":
    main()
