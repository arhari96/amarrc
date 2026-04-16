from django.db import models
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings

from django.core.files.base import ContentFile
from io import BytesIO
import os

import qrcode
import textwrap


class NewRc(models.Model):
    # Front fields
    reg_number = models.CharField(max_length=10, primary_key=True)
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

        # Create front image
        media_path_front = Path(settings.MEDIA_ROOT) / "front.png"
        img_front = Image.open(media_path_front, mode="r")
        d_front = ImageDraw.Draw(img_front)

        # Construct font paths
        bold_font_path = Path(settings.FONTS_ROOT) / "SourceSans3-Semibold.ttf"
        regular_font_path = Path(settings.FONTS_ROOT) / "Arial.ttf"

        bold = ImageFont.truetype(str(bold_font_path), size=22)
        font1 = ImageFont.truetype(str(regular_font_path), size=18)
        font2 = ImageFont.truetype(str(regular_font_path), size=18)

        draw_text_psd_style(
            d_front,
            (192, 99),
            self.reg_number,
            font=bold,
            tracking=-0.2,
            leading=6,
            fill=(14, 15, 15),
        )
        draw_text_psd_style(
            d_front,
            (192, 150),
            self.chassis_number,
            font=font1,
            tracking=-0.1,
            leading=8,
            fill=(14, 15, 15),
        )
        draw_text_psd_style(
            d_front,
            (192, 201),
            self.engine_number,
            font=font1,
            tracking=-0.1,
            leading=8,
            fill=(14, 15, 15),
        )
        draw_text_psd_style(
            d_front,
            (192, 254),
            self.name,
            font=font1,
            tracking=-0.1,
            leading=8,
            fill=(14, 15, 15),
        )
        draw_text_psd_style(
            d_front,
            (192, 307),
            self.son_of,
            font=font1,
            tracking=-0.1,
            leading=8,
            fill=(14, 15, 15),
        )
        draw_text_psd_style(
            d_front,
            (192, 351),
            self.street_name,
            font=font2,
            tracking=-0.1,
            leading=8,
            fill=(14, 15, 15),
        )
        draw_text_psd_style(
            d_front,
            (192, 370),
            self.city,
            font=font2,
            tracking=-0.1,
            leading=8,
            fill=(14, 15, 15),
        )
        draw_text_psd_style(
            d_front,
            (192, 389),
            self.district,
            font=font2,
            tracking=-0.1,
            leading=8,
            fill=(14, 15, 15),
        )
        if self.district1:
            draw_text_psd_style(
                d_front,
                (192, 408),
                self.district1,
                font=font2,
                tracking=-0.1,
                leading=8,
                fill=(14, 15, 15),
            )
        draw_text_psd_style(
            d_front,
            (30, 322.0),
            self.fuel,
            font=font2,
            tracking=-0.1,
            leading=8,
            fill=(14, 15, 15),
        )
        draw_text_psd_style(
            d_front,
            (30, 370),
            self.emission_norms,
            font=font2,
            tracking=-0.1,
            leading=8,
            fill=(14, 15, 15),
        )
        draw_text_psd_style(
            d_front,
            (598.01, 153),
            self.serial,
            font=font2,
            tracking=-0.1,
            leading=8,
            fill=(14, 15, 15),
        )
        draw_text_psd_style(
            d_front,
            (380.01, 105.1),
            self.reg_date,
            font=font2,
            tracking=-0.1,
            leading=8,
            fill=(14, 15, 15),
        )
        draw_text_psd_style(
            d_front,
            (542.01, 105.1),
            self.reg_valid,
            font=font2,
            tracking=-0.1,
            leading=8,
            fill=(14, 15, 15),
        )

        angle = 90
        im = Image.new("RGBA", (100, 60), (255, 255, 255, 0))
        draw = ImageDraw.Draw(im)
        bold_font_path = Path(settings.FONTS_ROOT) / "SourceSans3-Semibold.ttf"
        regular_font_path = Path(settings.FONTS_ROOT) / "Arial.ttf"
        # Create a larger bold font for issue_date to compensate for rotation
        issue_date_font = ImageFont.truetype(str(regular_font_path), size=18)
        draw.text((0, 0), self.issue_date, fill=(14, 15, 15), font=issue_date_font, stroke_width=0.5)
        rot = im.rotate(angle, expand=1)
        img_front.paste(rot, (648, 95), rot)

        img_io_front = BytesIO()
        img_front.save(img_io_front, format="PNG")
        img_io_front.seek(0)

        # Save the BytesIO object to the model's ImageField
        self.front_image.save(
            f"{self.reg_number}_front.png", ContentFile(img_io_front.read()), save=False
        )

        media_path_back = Path(settings.MEDIA_ROOT) / "back.png"
        img_back = Image.open(media_path_back, mode="r")

        bold_font_path = Path(settings.FONTS_ROOT) / "SourceSans3-Semibold.ttf"
        font_path = Path(settings.FONTS_ROOT) / "SourceSans3-Regular.ttf"

        bold = ImageFont.truetype(str(bold_font_path), 15)
        font = ImageFont.truetype(str(font_path), 15)
        d = ImageDraw.Draw(img_back)
        d.text(
            (36, 98), self.reg_number, fill=(14, 15, 15), font=bold, stroke_fill="black"
        )
        d.text(
            (36, 276),
            self.month_year_of_Mfg,
            fill=(14, 15, 15),
            font=font,
            stroke_fill="black",
        )
        d.text(
            (36, 312),
            self.number_cylinder,
            fill=(14, 15, 15),
            font=font,
            stroke_fill="black",
        )
        if self.number_of_Axle:
            d.text(
                (36, 354),
                self.number_of_Axle,
                fill=(14, 15, 15),
                font=font,
                stroke_fill="black",
            )
        d.text(
            (288, 39),
            self.vehicle_class,
            fill=(14, 15, 15),
            font=font,
            stroke_fill="black",
        )
        d.text(
            (193, 85),
            self.maker_name,
            fill=(14, 15, 15),
            font=font,
            stroke_fill="black",
        )
        d.text(
            (193, 122),
            self.model_name,
            fill=(14, 15, 15),
            font=font,
            stroke_fill="black",
        )
        d.text(
            (193, 158), self.color, fill=(14, 15, 15), font=font, stroke_fill="black"
        )
        d.text(
            (193, 197),
            self.body_type,
            fill=(14, 15, 15),
            font=font,
            stroke_fill="black",
        )
        d.text(
            (193, 234), self.seating, fill=(14, 15, 15), font=font, stroke_fill="black"
        )
        d.text(
            (193, 274), self.unladen, fill=(14, 15, 15), font=font, stroke_fill="black"
        )
        d.text(
            (270, 274), self.laden, fill=(14, 15, 15), font=font, stroke_fill="black"
        )
        d.text(
            (193, 314), self.cubic, fill=(14, 15, 15), font=font, stroke_fill="black"
        )
        d.text(
            (300, 314),
            self.horse_power,
            fill=(14, 15, 15),
            font=font,
            stroke_fill="black",
        )
        d.text(
            (458, 314),
            self.wheel_base,
            fill=(14, 15, 15),
            font=font,
            stroke_fill="black",
        )
        if self.standing:
            d.text(
                (300, 234),
                self.standing,
                fill=(14, 15, 15),
                font=font,
                stroke_fill="black",
            )
        if self.sleeper:
            d.text(
                (345, 234),
                self.sleeper,
                fill=(14, 15, 15),
                font=font,
                stroke_fill="black",
            )
        if self.gross_combination:
            d.text(
                (335, 274),
                self.gross_combination,
                fill=(14, 15, 15),
                font=font,
                stroke_fill="black",
            )
        if self.rto_name:
            d.text(
                (468, 395),
                self.rto_name,
                fill=(14, 15, 15),
                font=font,
                stroke_fill="black",
            )
        if self.financer:
            textwrapped = textwrap.wrap(self.financer, width=20)
            d.text(
                (193, 352),
                "\n".join(textwrapped),
                fill=(14, 15, 15),
                font=font,
                stroke_fill="black",
            )
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
        media_path_front = Path(settings.MEDIA_ROOT) / "front.png"
        img_front = Image.open(media_path_front, mode="r")
        d_front = ImageDraw.Draw(img_front)

        bold_font_front = Path(settings.FONTS_ROOT) / "SourceSans3-Semibold.ttf"
        bold = ImageFont.truetype(
            str(bold_font_front),
            size=26,
        )
        font1 = ImageFont.truetype(
            str(bold_font_front),
            size=18,
        )
        font2 = ImageFont.truetype(
            str(bold_font_front),
            size=18,
        )
        d_front.text(
            (206, 97),
            self.reg_number,
            fill=(14, 15, 15),
            font=bold,
            stroke_fill="black",
        )
        d_front.text(
            (208, 150),
            self.chassis_number,
            fill=(14, 15, 15),
            font=font1,
            stroke_fill="black",
        )
        d_front.text(
            (208.09, 196.1),
            self.engine_number,
            fill=(14, 15, 15),
            font=font1,
            stroke_fill="black",
        )
        d_front.text(
            (207.01, 237), self.name, fill=(14, 15, 15), font=font1, stroke_fill="black"
        )
        d_front.text(
            (207.01, 282),
            self.son_of,
            fill=(14, 15, 15),
            font=font1,
            stroke_fill="black",
        )
        d_front.text(
            (200.01, 341),
            self.street_name,
            fill=(14, 15, 15),
            font=font2,
            stroke_fill="black",
        )
        d_front.text(
            (200.01, 361), self.city, fill=(14, 15, 15), font=font2, stroke_fill="black"
        )
        d_front.text(
            (200.01, 380),
            self.district,
            fill=(14, 15, 15),
            font=font2,
            stroke_fill="black",
        )

        if self.district1:
            d_front.text(
                (200.01, 395),
                self.district1,
                fill=(14, 15, 15),
                font=font2,
                stroke_fill="black",
            )

        if self.fuel:
            d_front.text(
                (43.01, 274.1),
                self.fuel,
                fill=(14, 15, 15),
                font=font1,
                stroke_fill="black",
            )

        d_front.text(
            (467.01, 103.1),
            self.reg_date,
            fill=(14, 15, 15),
            font=font1,
            stroke_fill="black",
        )
        d_front.text(
            (516.01, 151.1),
            self.reg_valid,
            fill=(14, 15, 15),
            font=font1,
            stroke_fill="black",
        )
        d_front.text(
            (598.01, 193.1),
            self.serial,
            fill=(14, 15, 15),
            font=font1,
            stroke_fill="black",
        )

        angle = 90
        im = Image.new("RGBA", (100, 60), 0)
        draw = ImageDraw.Draw(im)
        draw.text((0, 0), self.owner_type, fill=(14, 15, 15), font=font1, size=14)

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
        wpercent = 125 / float(qr_from.size[0])
        hsize = int((float(qr_from.size[1]) * float(wpercent)))
        qr_from = qr_from.resize((125, hsize), Image.LANCZOS)

        rot = im.rotate(angle, expand=1)
        img_front.paste(qr_from, (517, 255))
        img_front.paste(rot, (639, 152))

        img_io_front = BytesIO()
        img_front.save(img_io_front, format="PNG")
        img_io_front.seek(0)
        self.front_image.save(
            f"{self.reg_number}_front.png", ContentFile(img_io_front.read()), save=False
        )

    def create_back_image(self):
        media_path_back = Path(settings.MEDIA_ROOT) / "back.png"
        img_back = Image.open(media_path_back, mode="r")
        d_back = ImageDraw.Draw(img_back)
        bold_font_path = Path(settings.FONTS_ROOT) / "SourceSans3-Semibold.ttf"
        regular_font_path = Path(settings.FONTS_ROOT) / "SourceSans3-Regular.ttf"
        bold = ImageFont.truetype(str(bold_font_path), size=17)
        font = ImageFont.truetype(str(regular_font_path), size=18)
        d_back.text(
            (226, 48), self.type, fill=(14, 15, 15), font=bold, stroke_fill="black"
        )
        d_back.text(
            (40, 93), self.reg_number, fill=(14, 15, 15), font=font, stroke_fill="black"
        )
        d_back.text(
            (40, 134),
            self.month_year_of_Mfg,
            fill=(14, 15, 15),
            font=font,
            stroke_fill="black",
        )
        d_back.text(
            (40, 174), self.wheel_base, fill=(14, 15, 15), font=font, stroke_fill="black"
        )
        d_back.text(
            (40, 213), self.cubic, fill=(14, 15, 15), font=font, stroke_fill="black"
        )
        d_back.text(
            (40, 253), self.number_cylinder, fill=(14, 15, 15), font=font, stroke_fill="black"
        )
        d_back.text(
            (40, 315),
            self.ledan_unledan,
            fill=(14, 15, 15),
            font=font,
            stroke_fill="black",
        )
        d_back.text(
            (196, 93), self.maker_name, fill=(14, 15, 15), font=font, stroke_fill="black"
        )
        d_back.text(
            (196, 134), self.model_name, fill=(14, 15, 15), font=font, stroke_fill="black"
        )
        d_back.text(
            (196, 174), self.color, fill=(14, 15, 15), font=font, stroke_fill="black"
        )
        d_back.text(
            (196, 213),
            self.body_type,
            fill=(14, 15, 15),
            font=font,
            stroke_fill="black",
        )
        d_back.text(
            (196, 253), self.seating, fill=(14, 15, 15), font=font, stroke_fill="black"
        )
        d_back.text(
            (196, 298),
            self.tax_valid,
            fill=(14, 15, 15),
            font=font,
            stroke_fill="black",
        )
        if self.rto_name:
            d_back.text(
                (445, 399), self.rto_name, fill=(14, 15, 15), font=font, stroke_fill="black"
            )
        if self.financer:
            textwrapped = textwrap.wrap(self.financer, width=20)
            d_back.text(
                (455, 259),
                "\n".join(textwrapped),
                fill=(14, 15, 15),
                font=font,
                stroke_fill="black",
            )
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