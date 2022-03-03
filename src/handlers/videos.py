import os
from uuid import uuid4

import cv2
import ffmpeg
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CommandHandler, ConversationHandler, Filters, MessageHandler

from src import current_bot
from src.helpers import rescale_frame


def get_strategy(update, context):
    user = update.effective_user
    user.send_message(
        "Choose strategy:",
        reply_markup=ReplyKeyboardMarkup(
            [["Downscale"], ["H265 codec with sound"]],
            resize_keyboard=True,
            one_time_keyboard=True,
        ),
    )

    file_id = update.message.video.file_id
    context.user_data["file_id"] = file_id

    return 1


@current_bot.log_update
def ask_downscale_percent(update, context):
    user = update.effective_user
    user.send_message(
        "Enter resolution scale (integer from 1 to 99)",
        reply_markup=ReplyKeyboardRemove(),
    )

    return 2


@current_bot.log_update
def downscale_video(update, context):
    user = update.effective_user
    user.send_message("Downloading...")

    percent = int(update.message.text)

    filename = uuid4().hex
    video_file = f"media/{filename}.mp4"
    rescaled_video_file = f"media/{filename}.rescaled.mkv"

    file_id = context.user_data["file_id"]
    file = current_bot.bot.get_file(file_id)
    file.download(video_file)

    user.send_message("Downscaling...")

    capture = cv2.VideoCapture(video_file)

    try:
        if not capture.isOpened():
            raise FileNotFoundError

        ret, frame = capture.read()

        rescaled_frame = rescale_frame(frame, percent)
        (h, w) = rescaled_frame.shape[:2]
        fps = capture.get(cv2.CAP_PROP_FPS) or 30

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(rescaled_video_file, fourcc, fps, (w, h), True)

        while capture.isOpened():
            ret, frame = capture.read()

            if not ret:
                break

            rescaled_frame = rescale_frame(frame, percent)
            writer.write(rescaled_frame)

        capture.release()
        writer.release()

        user.send_document(
            document=open(rescaled_video_file, "rb"), filename="downscaled.mkv"
        )

    except Exception as ex:
        raise ex

    finally:
        os.remove(video_file)
        os.remove(rescaled_video_file)

    return ConversationHandler.END


@current_bot.log_update
def ask_h265_crf(update, context):
    user = update.effective_user
    user.send_message(
        "Enter CRF value for H265 codec "
        "(integer from 0 to 51, where 0 is max quality).\n"
        "Optimal values are between 18 and 28",
        reply_markup=ReplyKeyboardRemove(),
    )

    return 3


@current_bot.log_update
def h265_with_sound_video(update, context):
    user = update.effective_user
    user.send_message("Downloading...")

    crf = int(update.message.text)

    filename = uuid4().hex
    video_file = f"media/{filename}.mp4"
    rescaled_video_file = f"media/{filename}.rescaled.mkv"

    file_id = context.user_data["file_id"]
    file = current_bot.bot.get_file(file_id)
    file.download(video_file)

    user.send_message("Downscaling...")

    try:
        (
            ffmpeg.input(video_file)
            .output(rescaled_video_file, vcodec="libx265", crf=crf, acodec="libopus")
            .run()
        )

        user.send_document(
            document=open(rescaled_video_file, "rb"), filename="downscaled.mkv"
        )
        user.send_message(
            f"{os.path.getsize(video_file)} bytes -> "
            f"{os.path.getsize(rescaled_video_file)} bytes"
        )

    except Exception as ex:
        raise ex

    finally:
        os.remove(video_file)
        os.remove(rescaled_video_file)

    return ConversationHandler.END


@current_bot.log_update
def cancel(update, context):
    user = update.effective_user
    user.send_message("Okay, smartass...")

    return ConversationHandler.END


current_bot.dispatcher.add_handler(
    ConversationHandler(
        entry_points=[MessageHandler(Filters.video, get_strategy)],
        states={
            1: [
                MessageHandler(Filters.regex(r"^Downscale$"), ask_downscale_percent),
                MessageHandler(Filters.regex(r"^H265 codec with sound$"), ask_h265_crf),
            ],
            2: [MessageHandler(Filters.regex(r"^[1-9][0-9]?$"), downscale_video)],
            3: [MessageHandler(Filters.regex(r"^\d+$"), h265_with_sound_video)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )
)
