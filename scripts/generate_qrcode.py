import os
import qrcode

BASE_FRONT_URL = os.getenv("BASE_FRONT_URL", "http://127.0.0.1:5173")
START = int(os.getenv("MESA_START", "1"))
END = int(os.getenv("MESA_END", "20"))
OUT_DIR = os.getenv("OUT_DIR", "qr")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    for mesa in range(START, END + 1):
        url = f"{BASE_FRONT_URL}/?mesa={mesa}"
        img = qrcode.make(url)

        filename = os.path.join(OUT_DIR, f"mesa-{mesa:02d}.png")
        img.save(filename)

    print(f"Gerado: {OUT_DIR}/mesa-XX.png (mesas {START}..{END})")
    print(f"Base URL: {BASE_FRONT_URL}")


if __name__ == "__main__":
    main()
