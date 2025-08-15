from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import random

user_data = {}

def delitelji(n):
    return sorted(list(set([i for i in range(1, int(n**0.5) + 1) if n % i == 0 for j in (i, n // i)] if n > 0 else [])))

# ==== KORAK 1: Izbira načina ====
async def choose_mode(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    chat_id = update.effective_chat.id
    if text in ["izmisli", "uganiš"]:
        user_data[chat_id]["mode"] = text
        if text == "izmisli":
            await start_izmisli(update, context)
        elif text == "uganiš":
            await start_uganis(update, context)
    else:
        await update.message.reply_text("Prosim izberi 'izmisli' ali 'uganiš'.")

# ==== "IZMISLI" način ====
async def start_izmisli(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Vnesi dve naravni številki, ločeni s presledkom.")

async def guess_izmisli(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    chat_id = update.effective_chat.id

    # Če še nimamo deliteljev, jih prvič izračunamo
    if "delitelji" not in user_data[chat_id]:
        try:
            stevili = sorted(list(map(int, text.split())))
            razlika = stevili[1] - stevili[0]
            de = delitelji(razlika)
            user_data[chat_id]["delitelji"] = de
            await update.message.reply_text(f"Ali je modul večji, manjši ali enak {de[len(de)//2]}? (>, <, =)")
        except:
            await update.message.reply_text("Prosim vnesi dve pravilni številki, ločeni s presledkom.")
        return

    # Če že ugibamo
    de = user_data[chat_id]["delitelji"]
    pol = len(de) // 2

    if text == ">":
        de = de[pol+1:]
    elif text == "<":
        de = de[:pol]
    elif text == "=":
        await update.message.reply_text("JJUUPPII!!!!! UGANIL SEM TVOJ MODUL!!!!")
        await update.message.reply_text("🎉")
        await update.message.reply_text("Za naslednjo igro napišite /start.")
        user_data.pop(chat_id, None)
        return
    else:
        await update.message.reply_text("Prosim uporabi samo >, < ali =.")
        return

    if not de:
        await update.message.reply_text("Zmotil si se, saj je bila to zadnja možnost.")
        user_data.pop(chat_id, None)
        return
    user_data[chat_id]["delitelji"] = de
    await update.message.reply_text(f"Vsi ostali delitelji so {de}")
    await update.message.reply_text(f"Ali je modul večji, manjši ali enak {de[len(de)//2]}? (>, <, =)")

# ==== "UGANIŠ" način ====
async def start_uganis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    modul = random.randint(1, 1000)
    stena = modul * random.randint(1, 50)
    stdva = modul * random.randint(1, 50)
    user_data[chat_id]["modul"] = modul
    await update.message.reply_text(f"Moj modul je delitelj {stena} in {stdva}. Ga boš uganil?")

async def guess_uganis(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    chat_id = update.effective_chat.id
    try:
        guess = int(text)
    except ValueError:
        await update.message.reply_text("Prosim vnesi celo število.")
        return

    modul = user_data[chat_id]["modul"]
    if guess > modul:
        await update.message.reply_text("Modul je manjši.")
    elif guess < modul:
        await update.message.reply_text("Modul je večji.")
    else:
        await update.message.reply_text("Uganil si modul!!! Čestitke!!")
        await update.message.reply_text("🎊")
        await update.message.reply_text("👍")
        await update.message.reply_text("Za naslednjo igro napišite /start.")
        user_data.pop(chat_id, None)

# ==== START KOMANDA ====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data[update.effective_chat.id] = {}
    reply_keyboard = [["izmisli", "uganiš"]]
    await update.message.reply_text("🤖")
    await update.message.reply_text(
        "Kateri način igre želiš igrati? Napiši izmisli, če želiš, da jaz uganem, ali uganiš, če želiš uganiti ti.",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )

# ==== GLAVNI MESSAGE HANDLER ====
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text.strip().lower()

    # Če uporabnik še ni izbral načina
    if "mode" not in user_data.get(chat_id, {}):
        await choose_mode(update, context, text)
        return

    # Glede na način igre
    if user_data[chat_id]["mode"] == "izmisli":
        await guess_izmisli(update, context, text)
    elif user_data[chat_id]["mode"] == "uganiš":
        await guess_uganis(update, context, text)

# ==== MAIN ====
def main():
    app = ApplicationBuilder().token("8452775735:AAEe2-cF1mZvewgDBfQlZ9Aj9gVKHAyziS0").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.run_polling()

if __name__ == "__main__":
    main()