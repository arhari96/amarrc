from django.db import models
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings

from django.core.files.base import ContentFile
from io import BytesIO
import os

import qrcode
import textwrap


# Create your models here.
class FrontRcNew(models.Model):
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
    fuel = models.CharField(max_length=6)
    serial = models.CharField(max_length=2)
    emission_norms = models.CharField(max_length=20)
    issue_date = models.CharField(max_length=20)

    now = models.DateField(auto_now_add=True, auto_created=True)
    image = models.ImageField(upload_to="front_rc_new_images/", null=True, blank=True)

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

        # Use settings.MEDIA_ROOT to construct the file path
        media_path = Path(settings.MEDIA_ROOT) / "front.png"
        img = Image.open(media_path, mode="r")
        d = ImageDraw.Draw(img)

        # Construct font paths
        bold_font_path = Path(settings.FONTS_ROOT) / "SourceSans3-Semibold.ttf"
        regular_font_path = Path(settings.FONTS_ROOT) / "Arial.ttf"

        bold = ImageFont.truetype(str(bold_font_path), size=22)
        font1 = ImageFont.truetype(str(regular_font_path), size=18)
        font2 = ImageFont.truetype(str(regular_font_path), size=18)

        draw_text_psd_style(
            d,
            (192, 97),
            self.reg_number,
            font=bold,
            tracking=-0.2,
            leading=6,
            fill=(14, 15, 15),
        )
        draw_text_psd_style(
            d,
            (192, 148),
            self.chassis_number,
            font=font1,
            tracking=-0.1,
            leading=8,
            fill=(14, 15, 15),
        )
        draw_text_psd_style(
            d,
            (192, 199),
            self.engine_number,
            font=font1,
            tracking=-0.1,
            leading=8,
            fill=(14, 15, 15),
        )
        draw_text_psd_style(
            d,
            (192, 252),
            self.name,
            font=font1,
            tracking=-0.1,
            leading=8,
            fill=(14, 15, 15),
        )
        draw_text_psd_style(
            d,
            (192, 305),
            self.son_of,
            font=font1,
            tracking=-0.1,
            leading=8,
            fill=(14, 15, 15),
        )
        draw_text_psd_style(
            d,
            (192, 349),
            self.street_name,
            font=font2,
            tracking=-0.1,
            leading=8,
            fill=(14, 15, 15),
        )
        draw_text_psd_style(
            d,
            (192, 368),
            self.city,
            font=font2,
            tracking=-0.1,
            leading=8,
            fill=(14, 15, 15),
        )
        draw_text_psd_style(
            d,
            (192, 387),
            self.district,
            font=font2,
            tracking=-0.1,
            leading=8,
            fill=(14, 15, 15),
        )
        if self.district1:
            draw_text_psd_style(
                d,
                (192, 406),
                self.district1,
                font=font2,
                tracking=-0.1,
                leading=8,
                fill=(14, 15, 15),
            )
        draw_text_psd_style(
            d,
            (30, 320.0),
            self.fuel,
            font=font2,
            tracking=-0.1,
            leading=8,
            fill=(14, 15, 15),
        )
        draw_text_psd_style(
            d,
            (30, 368),
            self.emission_norms,
            font=font2,
            tracking=-0.1,
            leading=8,
            fill=(14, 15, 15),
        )
        draw_text_psd_style(
            d,
            (598.01, 151),
            self.serial,
            font=font2,
            tracking=-0.1,
            leading=8,
            fill=(14, 15, 15),
        )
        draw_text_psd_style(
            d,
            (380.01, 103.1),
            self.reg_date,
            font=font2,
            tracking=-0.1,
            leading=8,
            fill=(14, 15, 15),
        )
        draw_text_psd_style(
            d,
            (542.01, 103.1),
            self.reg_valid,
            font=font2,
            tracking=-0.1,
            leading=8,
            fill=(14, 15, 15),
        )

        angle = 90
        im = Image.new("RGBA", (100, 60), (255, 255, 255, 0))
        draw = ImageDraw.Draw(im)
        draw.text((0, 0), self.issue_date, fill=(14, 15, 15), font=font1, size=14)
        rot = im.rotate(angle, expand=1)
        img.paste(rot, (648, 95), rot)

        img_io = BytesIO()
        img.save(img_io, format="PNG")
        img_io.seek(0)

        # Save the BytesIO object to the model's ImageField
        self.image.save(
            f"{self.reg_number}_front.png", ContentFile(img_io.read()), save=False
        )

        super(FrontRcNew, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super(FrontRcNew, self).delete(*args, **kwargs)

    def __str__(self):
        return f"{self.name} {self.reg_number}"


class BackRcNew(models.Model):
    reg_number = models.CharField(max_length=10, primary_key=True)
    reg_date = models.CharField(max_length=50, default="01-01-2023")
    month_year_of_Mfg = models.CharField(max_length=15)
    number_cylinder = models.CharField(max_length=2)        
    number_of_Axle = models.CharField(
        max_length=2,
        blank=True,
        null=True,
    )
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
    financer = models.CharField(max_length=25, blank=True, null=True)
    rto_name = models.CharField(max_length=50, blank=True, null=True)
    now = models.DateField(auto_now_add=True, auto_created=True)
    image = models.ImageField(upload_to="back_rc_new_images/", blank=True, null=True)
    chassis_number = models.CharField(max_length=27, default="chassisnumber")
    engine_number = models.CharField(max_length=20, default="enginenumber")
    name = models.CharField(max_length=40)

    class Meta:
        ordering = ("-now",)

    def save(self, *args, **kwargs):
        media_path = Path(settings.MEDIA_ROOT) / "back.png"
        img = Image.open(media_path, mode="r")

        bold_font_path = Path(settings.MEDIA_ROOT) / "fonts/SourceSans3-Semibold.ttf"
        font_path = Path(settings.MEDIA_ROOT) / "fonts/SourceSans3-Regular.ttf"

        bold = ImageFont.truetype(str(bold_font_path), 15)
        font = ImageFont.truetype(str(font_path), 15)
        d = ImageDraw.Draw(img)
        d.text(
            (36, 96), self.reg_number, fill=(14, 15, 15), font=bold, stroke_fill="black"
        )
        d.text(
            (36, 274),
            self.month_year_of_Mfg,
            fill=(14, 15, 15),
            font=font,
            stroke_fill="black",
        )
        d.text(
            (36, 310),
            self.number_cylinder,
            fill=(14, 15, 15),
            font=font,
            stroke_fill="black",
        )
        if self.number_of_Axle:
            d.text(
                (36, 352),
                self.number_of_Axle,
                fill=(14, 15, 15),
                font=font,
                stroke_fill="black",
            )
        d.text(
            (288, 37),
            self.vehicle_class,
            fill=(14, 15, 15),
            font=font,
            stroke_fill="black",
        )
        d.text(
            (193, 83),
            self.maker_name,
            fill=(14, 15, 15),
            font=font,
            stroke_fill="black",
        )
        d.text(
            (193, 120),
            self.model_name,
            fill=(14, 15, 15),
            font=font,
            stroke_fill="black",
        )
        d.text(
            (193, 156), self.color, fill=(14, 15, 15), font=font, stroke_fill="black"
        )
        d.text(
            (193, 195),
            self.body_type,
            fill=(14, 15, 15),
            font=font,
            stroke_fill="black",
        )
        d.text(
            (193, 232), self.seating, fill=(14, 15, 15), font=font, stroke_fill="black"
        )
        d.text(
            (193, 272), self.unladen, fill=(14, 15, 15), font=font, stroke_fill="black"
        )
        d.text(
            (265, 272), self.laden, fill=(14, 15, 15), font=font, stroke_fill="black"
        )
        d.text(
            (193, 312), self.cubic, fill=(14, 15, 15), font=font, stroke_fill="black"
        )
        d.text(
            (300, 312),
            self.horse_power,
            fill=(14, 15, 15),
            font=font,
            stroke_fill="black",
        )
        d.text(
            (458, 312),
            self.wheel_base,
            fill=(14, 15, 15),
            font=font,
            stroke_fill="black",
        )
        if self.standing:
            d.text(
                (300, 232),
                self.standing,
                fill=(14, 15, 15),
                font=font,
                stroke_fill="black",
            )
        if self.sleeper:
            d.text(
                (325, 272),
                self.sleeper,
                fill=(14, 15, 15),
                font=font,
                stroke_fill="black",
            )
        if self.gross_combination:
            d.text(
                (250, 272),
                self.gross_combination,
                fill=(14, 15, 15),
                font=font,
                stroke_fill="black",
            )
        if self.rto_name:
            d.text(
                (468, 393),
                self.rto_name,
                fill=(14, 15, 15),
                font=font,
                stroke_fill="black",
            )
        if self.financer:
            textwrapped = textwrap.wrap(self.financer, width=20)
            d.text(
                (193, 350),
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
        qr_from = qr_from.resize((125, hsize), Image.ANTIALIAS)
        img.paste(qr_from, (32, 122))

        img_io = BytesIO()
        img.save(img_io, format="PNG")
        img_io.seek(0)

        self.image.save(
            f"{self.reg_number}_back.png", ContentFile(img_io.read()), save=False
        )

        super(BackRcNew, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super(FrontRcNew, self).delete(*args, **kwargs)

    def __str__(self):
        return f"{self.rto_name} {self.reg_number}"
