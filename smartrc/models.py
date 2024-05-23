from django.db import models
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings

from django.core.files.base import ContentFile
from io import BytesIO
import os


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
    image = models.ImageField(upload_to="front_rc_images/", null=True, blank=True)

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
