from django.db import models
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings

from django.core.files.base import ContentFile
from io import BytesIO
import os

import qrcode
import textwrap


def font_path(*filenames):
    search_roots = [
        Path(settings.FONTS_ROOT),
        Path(settings.BASE_DIR) / "arial",
    ]
    for filename in filenames:
        for root in search_roots:
            candidate = root / filename
            if candidate.exists():
                return candidate
    return search_roots[0] / filenames[0]


RC_FRONT_BOLD_FONT = ("ARIALBD.TTF", "Arial-BoldMT.ttf")
RC_FRONT_REGULAR_FONT = ("ARIAL.TTF", "Arial.ttf")
RC_FRONT_NARROW_FONT = ("ARIALN.TTF", "Arial.ttf")
RC_BACK_BOLD_FONT = "SourceSans3-Semibold.ttf"
RC_BACK_REGULAR_FONT = "SourceSans3-Regular.ttf"

TEMPLATE_REGISTRY = {
    "NT_TN": {
        "front": "nt_tn_front_empty.png",
        "back":  "nt_tn_back_empty.png",
    },
    "RC_WHITE": {
        "front": "rc_white_front_empty.png",
        "back":  "rc_white_back_empty.png",
    },
}


class NewRc(models.Model):
    # Front fields
    reg_number = models.CharField(max_length=10, primary_key=True)
    template = models.CharField(max_length=50, default="NT_TN", blank=True)
    chassis_number = models.CharField(max_length=27)
    engine_number = models.CharField(max_length=20)
    name = models.CharField(max_length=40)
    son_of = models.CharField(max_length=40)
    street_name = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    district1 = models.CharField(max_length=50, null=True, blank=True)
    reg_date = models.CharField(max_length=50)
    reg_valid = models.CharField(max_length=50)
    fuel = models.CharField(max_length=50)
    serial = models.CharField(max_length=2)
    emission_norms = models.CharField(max_length=20)
    issue_date = models.CharField(max_length=20)

    # Back fields
    month_year_of_Mfg = models.CharField(max_length=15)
    number_cylinder = models.CharField(max_length=2)
    number_of_Axle = models.CharField(max_length=2, blank=True, null=True)
    vehicle_class = models.CharField(max_length=75)
    maker_name = models.CharField(max_length=75)
    model_name = models.CharField(max_length=75)
    color = models.CharField(max_length=50)
    body_type = models.CharField(max_length=50)
    seating = models.CharField(max_length=50)
    standing = models.CharField(max_length=15, blank=True, null=True)
    sleeper = models.CharField(max_length=15, blank=True, null=True)
    unladen = models.CharField(max_length=15)
    laden = models.CharField(max_length=15)
    gross_combination = models.CharField(max_length=15, blank=True, null=True)
    cubic = models.CharField(max_length=15)
    horse_power = models.CharField(max_length=15)
    wheel_base = models.CharField(max_length=15)
    financer = models.CharField(max_length=50, blank=True, null=True)
    rto_name = models.CharField(max_length=50, blank=True, null=True)

    now = models.DateField(auto_now_add=True, auto_created=True)
    front_image = models.ImageField(
        upload_to="front_rc_new_images/", null=True, blank=True
    )
    back_image = models.ImageField(
        upload_to="back_rc_new_images/", blank=True, null=True
    )

    class Meta:
        ordering = ("-now",)

    def save(self, *args, **kwargs):
        def draw_text_psd_style(
            draw, xy, text, font, tracking=0, leading=None, **kwargs
        ):
            def stutter_chunk(lst, size, overlap=0, default=None):
                for i in range(0, len(lst), size - overlap):
                    r = list(lst[i : i + size])
                    while len(r) < size:
                        r.append(default)
                    yield r

            x, y = xy
            font_size = font.size
            lines = text.splitlines()
            if leading is None:
                leading = font.size * 1.2
            for line in lines:
                for a, b in stutter_chunk(line, 2, 1, " "):
                    w = font.getlength(a + b) - font.getlength(b)
                    draw.text((x, y), a, font=font, **kwargs)
                    x += w + (tracking / 1000) * font_size
                y += leading
                x = xy[0]

        # Create front image — use self.template (user-selected for New RC)
        template_name = self.template if self.template in TEMPLATE_REGISTRY else "NT_TN"
        template_entry = TEMPLATE_REGISTRY[template_name]
        front_path = Path(settings.MEDIA_ROOT) / "templates" / template_entry["front"]
        if not front_path.exists():
            front_path = Path(settings.MEDIA_ROOT) / "front.png"

        img_front = Image.open(front_path).convert("RGBA").copy()
        if img_front.size != (677, 428):
            img_front = img_front.resize((677, 428), Image.LANCZOS)
        d_front = ImageDraw.Draw(img_front)

        # Construct font paths
        bold_font_path = font_path(*RC_FRONT_BOLD_FONT)
        regular_font_path = font_path(*RC_FRONT_REGULAR_FONT)
        narrow_font_path = font_path(*RC_FRONT_NARROW_FONT)
        black_font_path = font_path("ArialBlack.ttf", "ARIBLK.TTF", *RC_FRONT_BOLD_FONT)

        black_font = ImageFont.truetype(str(black_font_path), size=19)
        bold = ImageFont.truetype(str(bold_font_path), size=19)
        date_font = ImageFont.truetype(str(bold_font_path), size=19)
        font1 = ImageFont.truetype(str(regular_font_path), size=18)
        font2 = ImageFont.truetype(str(regular_font_path), size=18)
        address_font = ImageFont.truetype(str(narrow_font_path), size=18)

        d_front.text((190, 108), self.reg_number, fill=(14, 15, 15), font=bold)
        d_front.text((374, 112), self.reg_date, fill=(14, 15, 15), font=date_font)
        d_front.text((541, 110), self.reg_valid, fill=(14, 15, 15), font=date_font)
        d_front.text((191, 157), self.chassis_number, fill=(14, 15, 15), font=font1)
        d_front.text((190, 208), self.engine_number, fill=(14, 15, 15), font=font1)
        d_front.text((191, 260), self.name, fill=(14, 15, 15), font=font1)
        d_front.text((192, 312), self.son_of, fill=(14, 15, 15), font=font1)
        d_front.text((193, 361), self.street_name, fill=(14, 15, 15), font=address_font)
        d_front.text((194, 380), self.city, fill=(14, 15, 15), font=address_font)
        d_front.text((193, 396), self.district, fill=(14, 15, 15), font=address_font)
        if self.district1:
            d_front.text((193, 412), self.district1, fill=(14, 15, 15), font=address_font)
        d_front.text((14, 323), self.fuel, fill=(14, 15, 15), font=font2)
        d_front.text((15, 369), self.emission_norms, fill=(14, 15, 15), font=font2)
        d_front.text((587, 147), self.serial, fill=(14, 15, 15), font=font2)

        angle = 90
        im = Image.new("RGBA", (100, 60), (255, 255, 255, 0))
        draw = ImageDraw.Draw(im)
        regular_font_path = font_path(*RC_FRONT_REGULAR_FONT)
        issue_date_font = ImageFont.truetype(str(regular_font_path), size=18)
        draw.text((0, 0), self.issue_date, fill=(14, 15, 15), font=issue_date_font)
        rot = im.rotate(angle, expand=1)
        img_front.paste(rot, (637, 95), rot)

        img_io_front = BytesIO()
        img_front.save(img_io_front, format="PNG")
        img_io_front.seek(0)

        # Save the BytesIO object to the model's ImageField
        self.front_image.save(
            f"{self.reg_number}_front.png", ContentFile(img_io_front.read()), save=False
        )

        # Back image — use same template key as front
        back_path = Path(settings.MEDIA_ROOT) / "templates" / template_entry["back"]
        if not back_path.exists():
            back_path = Path(settings.MEDIA_ROOT) / "back.png"
        img_back = Image.open(back_path).convert("RGB").copy()
        if img_back.size != (677, 428):
            img_back = img_back.resize((677, 428), Image.LANCZOS)

        bold_font_path = font_path(RC_BACK_BOLD_FONT)
        back_font_path = font_path(RC_BACK_REGULAR_FONT)

        bold = ImageFont.truetype(str(bold_font_path), 15)
        font = ImageFont.truetype(str(back_font_path), 15)
        d = ImageDraw.Draw(img_back)
        d.text((34, 98), self.reg_number, fill=(14, 15, 15), font=bold)
        # NT_TN back: left column
        d.text((34, 279), self.month_year_of_Mfg, fill=(14, 15, 15), font=font)
        d.text((35, 319), self.number_cylinder,    fill=(14, 15, 15), font=font)
        if self.number_of_Axle:
            d.text((34, 362), self.number_of_Axle, fill=(14, 15, 15), font=font)
        # NT_TN back: top band vehicle class
        d.text((288, 41), self.vehicle_class, fill=(14, 15, 15), font=font)
        # NT_TN back: right column
        d.text((191, 86), self.maker_name,  fill=(14, 15, 15), font=font)
        d.text((191, 124), self.model_name,  fill=(14, 15, 15), font=font)
        d.text((191, 161), self.color,       fill=(14, 15, 15), font=font)
        d.text((193, 199), self.body_type,   fill=(14, 15, 15), font=font)
        seating_txt = self.seating
        if self.standing:
            seating_txt += f" / {self.standing}"
        if self.sleeper:
            seating_txt += f" / {self.sleeper}"
        d.text((193, 237), seating_txt, fill=(14, 15, 15), font=font)
        # NT_TN back: weight row
        d.text((192, 277), self.unladen, fill=(14, 15, 15), font=font)
        d.text((273, 278), self.laden,   fill=(14, 15, 15), font=font)
        if self.gross_combination:
            d.text((358, 279), self.gross_combination, fill=(14, 15, 15), font=font)
        # NT_TN back: cubic / hp / wheelbase row
        d.text((192, 319), self.cubic,       fill=(14, 15, 15), font=font)
        d.text((302, 319), self.horse_power, fill=(14, 15, 15), font=font)
        d.text((443, 321), self.wheel_base,  fill=(14, 15, 15), font=font)
        if self.financer:
            textwrapped = textwrap.wrap(self.financer, width=35)
            d.text((193, 365), "\n".join(textwrapped), fill=(14, 15, 15), font=font)
        if self.rto_name:
            d.text((485, 399), self.rto_name, fill=(14, 15, 15), font=font)
        qr = qrcode.QRCode(
            version=5,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=2.5,
            border=4,
        )
        qr.add_data(
            f"{self.reg_number},{self.reg_date},{self.engine_number},{self.chassis_number},{self.name},Registration No:{self.reg_number}\nRegistration Date:{self.reg_date}\nEngine No:{self.engine_number}\nChassis No:{self.chassis_number}\nClick URL to verify: https://qr.parivahan.gov.in/vq/qr?v=10423i3rHyHNguBu"
        )
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_img.save("QR.png")
        path = Path(f"QR.png")
        qr_from = Image.open(path, mode="r")
        wpercent = 125 / float(qr_from.size[0])
        hsize = int((float(qr_from.size[1]) * float(wpercent)))
        qr_from = qr_from.resize((125, hsize), Image.LANCZOS)
        img_back.paste(qr_from, (32, 122))

        img_io_back = BytesIO()
        img_back.save(img_io_back, format="PNG")
        img_io_back.seek(0)

        self.back_image.save(
            f"{self.reg_number}_back.png", ContentFile(img_io_back.read()), save=False
        )
        super(NewRc, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Delete the front image file if it exists
        if self.front_image:
            if os.path.isfile(self.front_image.path):
                os.remove(self.front_image.path)

        # Delete the back image file if it exists
        if self.back_image:
            if os.path.isfile(self.back_image.path):
                os.remove(self.back_image.path)

        super(NewRc, self).delete(*args, **kwargs)

    def __str__(self):
        return f"{self.name} {self.reg_number}"


class OldRc(models.Model):
    reg_number = models.CharField(max_length=10, primary_key=True)
    chassis_number = models.CharField(max_length=35)
    engine_number = models.CharField(max_length=35)
    name = models.CharField(max_length=40)
    son_of = models.CharField(max_length=40)
    street_name = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    district = models.CharField(max_length=50)
    district1 = models.CharField(max_length=50, null=True, blank=True)
    reg_date = models.CharField(max_length=50)
    reg_valid = models.CharField(max_length=50)
    fuel = models.CharField(max_length=50, null=True, blank=True)
    serial = models.CharField(max_length=2)
    owner_type = models.CharField(max_length=12)
    month_year_of_Mfg = models.CharField(max_length=20)
    type = models.CharField(max_length=200)
    wheel_base = models.CharField(max_length=20)
    cubic = models.CharField(max_length=20)
    number_cylinder = models.CharField(max_length=20)
    ledan_unledan = models.CharField(max_length=50)
    maker_name = models.CharField(max_length=50)
    model_name = models.CharField(max_length=50)
    color = models.CharField(max_length=50)
    body_type = models.CharField(max_length=50)
    seating = models.CharField(max_length=6)
    rto_name = models.CharField(max_length=50, blank=True, null=True)
    financer = models.CharField(max_length=50, blank=True, null=True)
    tax_valid = models.CharField(
        max_length=50, default="LIFE TIME", null=True, blank=True
    )
    now = models.DateField(auto_now_add=True, auto_created=True)
    front_image = models.ImageField(
        upload_to="front_rc_old_images/", blank=True, null=True
    )
    back_image = models.ImageField(
        upload_to="back_rc_old_images/", blank=True, null=True
    )

    class Meta:
        ordering = ("-now",)

    def save(self, *args, **kwargs):
        self.create_front_image()
        self.create_back_image()
        super(OldRc, self).save(*args, **kwargs)

    def create_front_image(self):
        # OldRc always uses RC_WHITE front template
        front_path = Path(settings.MEDIA_ROOT) / "templates" / TEMPLATE_REGISTRY["RC_WHITE"]["front"]
        if not front_path.exists():
            front_path = Path(settings.MEDIA_ROOT) / "front.png"

        img_front = Image.open(front_path).convert("RGBA").copy()
        if img_front.size != (677, 428):
            img_front = img_front.resize((677, 428), Image.LANCZOS)
        d_front = ImageDraw.Draw(img_front)
        front_text_fill = (8, 9, 9)
        front_y_offset = 5

        def draw_short_text(draw, xy, text, font, x_scale=0.94, **kwargs):
            stroke_width = kwargs.get("stroke_width", 0)
            bbox = draw.textbbox((0, 0), text, font=font, stroke_width=stroke_width)
            width = max(1, bbox[2] - bbox[0])
            height = max(1, bbox[3] - bbox[1])
            text_img = Image.new("RGBA", (width + 4, height + 4), (255, 255, 255, 0))
            text_draw = ImageDraw.Draw(text_img)
            text_draw.text((2 - bbox[0], 2 - bbox[1]), text, font=font, **kwargs)
            resized_width = max(1, int(text_img.width * x_scale))
            text_img = text_img.resize((resized_width, text_img.height), Image.LANCZOS)
            img_front.paste(text_img, (int(xy[0]), int(xy[1] + front_y_offset)), text_img)

        bold_font_front = font_path(*RC_FRONT_BOLD_FONT)
        regular_font_front = font_path(*RC_FRONT_REGULAR_FONT)
        narrow_font_front = font_path(*RC_FRONT_NARROW_FONT)

        bold = ImageFont.truetype(str(bold_font_front), size=19)
        font1 = ImageFont.truetype(str(regular_font_front), size=18)
        font2 = ImageFont.truetype(str(regular_font_front), size=18)
        address_font = ImageFont.truetype(str(narrow_font_front), size=18)
        # RC WHITE FRONT — calibrated coordinates (677×428)
        # Row: Reg. No. / Date of Reg.
        draw_short_text(d_front, (204, 101), self.reg_number, fill=(14, 15, 15), font=bold)
        draw_short_text(d_front, (461, 100), self.reg_date,   fill=front_text_fill, font=font1)
        # Row: Chassis No. / Reg. Valid Till
        draw_short_text(d_front, (206, 147), self.chassis_number, fill=front_text_fill, font=font1)
        draw_short_text(d_front, (518, 151), self.reg_valid,      fill=front_text_fill, font=font1)
        # Row: Engine No. / Owner Sr. No.
        draw_short_text(d_front, (209, 194), self.engine_number, fill=front_text_fill, font=font1)
        draw_short_text(d_front, (582, 191), self.serial,        fill=front_text_fill, font=font1)
        # Row: Owner Name
        draw_short_text(d_front, (209, 233), self.name,   fill=front_text_fill, font=font1)
        # Row: Son/Daughter/Wife of
        draw_short_text(d_front, (207, 281), self.son_of, fill=front_text_fill, font=font1)
        # Address rows
        draw_short_text(d_front, (207, 342), self.street_name, fill=front_text_fill, font=font1)
        draw_short_text(d_front, (207, 360), self.city,        fill=front_text_fill, font=font1)
        draw_short_text(d_front, (207, 379), self.district,    fill=front_text_fill, font=font1)
        if self.district1:
            draw_short_text(d_front, (207, 395), self.district1, fill=front_text_fill, font=font1)
        # Left side: Fuel Used
        if self.fuel:
            draw_short_text(d_front, (28, 278), self.fuel, fill=front_text_fill, font=font1)

        # RC White front: owner_type rotated text on right edge (Card Issue Date column)
        angle = 90
        im = Image.new("RGBA", (100, 60), (255, 255, 255, 0))
        draw = ImageDraw.Draw(im)
        draw.text((0, 0), self.owner_type, fill=(14, 15, 15), font=font1)

        qr = qrcode.QRCode(
            version=5,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=2.5,
            border=4,
        )
        qr.add_data(
            f'Reg No: {self.reg_number}, Reg Date: {self.reg_date}, Name: {self.name}, Engine No: {self.engine_number}, Chasis: {self.chassis_number}, Tax valid to: {"".join(e for e in self.reg_valid if e.isalnum())}'
        )
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_img.save("QR.png")
        path = Path("QR.png")
        qr_from = Image.open(path, mode="r")
        wpercent = 100 / float(qr_from.size[0])
        hsize = int((float(qr_from.size[1]) * float(wpercent)))
        qr_from = qr_from.resize((100, hsize), Image.LANCZOS)

        rot = im.rotate(angle, expand=1)
        # RC White front: QR code sits over the hologram/chip area on the lower-left
        img_front.paste(qr_from, (518, 275))
        # RC White front: owner_type on the right edge vertical strip
        img_front.paste(rot, (638, 200), rot)

        img_io_front = BytesIO()
        img_front.save(img_io_front, format="PNG")
        img_io_front.seek(0)
        self.front_image.save(
            f"{self.reg_number}_front.png", ContentFile(img_io_front.read()), save=False
        )

    def create_back_image(self):
        # OldRc always uses RC_WHITE back template
        back_path = Path(settings.MEDIA_ROOT) / "templates" / TEMPLATE_REGISTRY["RC_WHITE"]["back"]
        if not back_path.exists():
            back_path = Path(settings.MEDIA_ROOT) / "back.png"
        img_back = Image.open(back_path).convert("RGB").copy()
        if img_back.size != (677, 428):
            img_back = img_back.resize((677, 428), Image.LANCZOS)
        d_back = ImageDraw.Draw(img_back)
        bold_font_path = font_path(RC_BACK_BOLD_FONT)
        back_font_path = font_path(RC_BACK_REGULAR_FONT)
        bold = ImageFont.truetype(str(bold_font_path), size=15)
        font = ImageFont.truetype(str(back_font_path), size=15)
        # RC WHITE BACK — calibrated coordinates (677×428)
        # Top band: vehicle class value placed after the "Vehicle Class" label
        d_back.text((314, 27), self.type, fill=(14, 15, 15), font=font)
        # Left column
        d_back.text((34, 93), self.reg_number, fill=(14, 15, 15), font=bold)
        d_back.text((36, 131), self.month_year_of_Mfg, fill=(14, 15, 15), font=font)
        d_back.text((36, 172), self.wheel_base, fill=(14, 15, 15), font=font)
        d_back.text((37, 211), self.cubic, fill=(14, 15, 15), font=font)
        d_back.text((38, 251), self.number_cylinder, fill=(14, 15, 15), font=font)
        d_back.text((37, 316), self.ledan_unledan, fill=(14, 15, 15), font=font)
        d_back.text((195, 302), self.tax_valid, fill=(14, 15, 15), font=font)
        # Right column
        d_back.text((193, 92), self.maker_name, fill=(14, 15, 15), font=font)
        d_back.text((193, 136), self.model_name, fill=(14, 15, 15), font=font)
        d_back.text((194, 174), self.color, fill=(14, 15, 15), font=font)
        d_back.text((193, 212), self.body_type, fill=(14, 15, 15), font=font)
        d_back.text((195, 254), self.seating, fill=(14, 15, 15), font=font)
        if self.financer:
            textwrapped = textwrap.wrap(self.financer, width=28)
            d_back.text((466, 260), "\n".join(textwrapped), fill=(14, 15, 15), font=font)
        if self.rto_name:
            d_back.text((442, 398), self.rto_name, fill=(14, 15, 15), font=font)
        img_io_back = BytesIO()
        img_back.save(img_io_back, format="PNG")
        img_io_back.seek(0)
        self.back_image.save(
            f"{self.reg_number}_back.png", ContentFile(img_io_back.read()), save=False
        )

    def delete(self, *args, **kwargs):
        # Delete the front image file if it exists
        if self.front_image:
            if os.path.isfile(self.front_image.path):
                os.remove(self.front_image.path)

        # Delete the back image file if it exists
        if self.back_image:
            if os.path.isfile(self.back_image.path):
                os.remove(self.back_image.path)

        super(OldRc, self).delete(*args, **kwargs)

    def __str__(self):
        return f"{self.name} {self.reg_number}"


class Rc(models.Model):
    reg_number= models.CharField(max_length=10, primary_key=True)
    data = models.JSONField()

    now = models.DateField(auto_now_add=True, auto_created=True)
    def __str__(self):
        return f"{self.reg_number}"
