"""
Main training script for Rapiro SEADD Vision (Morphology only).
Converted from rapiro_seadd_vision.ipynb.
"""

import os
import sys

# Auto-configurar LD_LIBRARY_PATH para paquetes CUDA de pip en Linux
if sys.platform.startswith("linux") and not os.environ.get("_TF_GPU_CONFIGURED"):
    venv_paths = [p for p in sys.path if "site-packages" in p]
    nvidia_paths = []
    for base_path in venv_paths:
        nvidia_base = os.path.join(base_path, "nvidia")
        if os.path.isdir(nvidia_base):
            for root, dirs, files in os.walk(nvidia_base):
                if "lib" in dirs:
                    nvidia_paths.append(os.path.join(root, "lib"))
    if nvidia_paths:
        current_ld = os.environ.get("LD_LIBRARY_PATH", "")
        new_ld = ":".join(nvidia_paths)
        if current_ld:
            new_ld = f"{new_ld}:{current_ld}"
        os.environ["LD_LIBRARY_PATH"] = new_ld
        os.environ["_TF_GPU_CONFIGURED"] = "1"
        os.execv(sys.executable, [sys.executable] + sys.argv)

import zipfile
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Get directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SEED = 42
tf.random.set_seed(SEED)
np.random.seed(SEED)

# Configurar GPU en TensorFlow si está disponible
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        print(f"¡GPU detectada! Usando para entrenar: {[g.name for g in gpus]}")
    except RuntimeError as e:
        print(f"Error al inicializar la GPU: {e}")
else:
    print("No se detectó ninguna GPU compatible. Se usará la CPU.")

# Find ZIP file in script directory
NOMBRE_ZIP = os.path.join(BASE_DIR, "training-dataset.zip")
if not os.path.exists(NOMBRE_ZIP):
    # Fallback to search for any zip file in the directory
    zip_files = [f for f in os.listdir(BASE_DIR) if f.endswith(".zip")]
    if zip_files:
        NOMBRE_ZIP = os.path.join(BASE_DIR, zip_files[0])
        print(f"Zip por defecto no encontrado. Usando: {NOMBRE_ZIP}")
    else:
        print(f"Error: No se encontró ningún archivo .zip en: {BASE_DIR}")
        exit(1)

DESTINO_IMAGENES = os.path.join(BASE_DIR, "images")

print(f"Descomprimiendo {NOMBRE_ZIP} en {DESTINO_IMAGENES}...")
os.makedirs(DESTINO_IMAGENES, exist_ok=True)
with zipfile.ZipFile(NOMBRE_ZIP, 'r') as z:
    z.extractall(DESTINO_IMAGENES)

# Verificación de imágenes descomprimidas
extensiones = (".png", ".jpg", ".jpeg")
imagenes = []
for raiz, _, archivos in os.walk(DESTINO_IMAGENES):
    for a in archivos:
        if a.lower().endswith(extensiones):
            imagenes.append(os.path.join(raiz, a))

print(f"Imágenes encontradas tras descomprimir: {len(imagenes)}")
if len(imagenes) == 0:
    print("Error: No se encontraron imágenes en el archivo descomprimido.")
    exit(1)
print("Ejemplos:", [os.path.basename(p) for p in imagenes[:5]])

# Encontrar labels.csv
LABELS_CSV = os.path.join(BASE_DIR, "labels.csv")
if not os.path.isfile(LABELS_CSV):
    # Intentar buscar dentro de la carpeta de imágenes descomprimidas
    temp_csv = os.path.join(DESTINO_IMAGENES, "labels.csv")
    if os.path.isfile(temp_csv):
        LABELS_CSV = temp_csv
    else:
        # Buscar en cualquier subdirectorio
        found_csv = False
        for root, dirs, files in os.walk(DESTINO_IMAGENES):
            for file in files:
                if file.lower() == "labels.csv":
                    LABELS_CSV = os.path.join(root, file)
                    found_csv = True
                    break
            if found_csv:
                break

if not os.path.isfile(LABELS_CSV):
    # Buscar cualquier archivo CSV en la carpeta base o imágenes
    csv_files = [f for f in os.listdir(BASE_DIR) if f.endswith(".csv")]
    if csv_files:
        LABELS_CSV = os.path.join(BASE_DIR, csv_files[0])
    else:
        print("Error: No se encontró el archivo labels.csv.")
        exit(1)

print(f"Usando archivo de etiquetas: {LABELS_CSV}")

# Cargar y validar el CSV de etiquetas
df = pd.read_csv(LABELS_CSV)
df.columns = [c.strip().lower() for c in df.columns]
assert {"image_filename", "morphology"}.issubset(df.columns), \
    "El CSV debe tener columnas image_filename y morphology"

# Limpieza de valores (espacios, mayúsculas inconsistentes)
df["morphology"] = df["morphology"].astype(str).str.strip()

# Taxonomía EXACTA de la base de conocimiento (el orden define los índices de clase)
MORPH_CLASSES = ["macula", "papula", "ampolla", "escama", "engrosamiento"]

# Filas con etiqueta fuera de la taxonomía o vacías -> se descartan
valid = df["morphology"].isin(MORPH_CLASSES)
if (~valid).any():
    print("Filas con morfología no reconocida (se descartan):")
    print(df.loc[~valid, "morphology"].value_counts())
df = df[valid].copy()

# Determinar el directorio de imágenes real comparando con los nombres del CSV
sample_files = df["image_filename"].head(5).tolist()
found_dir = DESTINO_IMAGENES
for root, dirs, files in os.walk(DESTINO_IMAGENES):
    if any(f in files for f in sample_files):
        found_dir = root
        break
IMAGES_DIR = found_dir
print(f"Directorio de imágenes resuelto: {IMAGES_DIR}")

# Verificar que las imágenes existan en disco
df["path"] = df["image_filename"].apply(lambda f: os.path.join(IMAGES_DIR, f))
exists = df["path"].apply(os.path.isfile)
if (~exists).any():
    print(f"{(~exists).sum()} imágenes del CSV no se encontraron en disco (se descartan).")
df = df[exists].copy()

if len(df) == 0:
    print("Error: No quedaron imágenes usables para el entrenamiento.")
    exit(1)

# Índice de clase
df["label"] = df["morphology"].map({c: i for i, c in enumerate(MORPH_CLASSES)})

print(f"\nTotal de imágenes etiquetadas usables: {len(df)}")
print("Conteo por clase:")
print(df["morphology"].value_counts().reindex(MORPH_CLASSES).fillna(0).astype(int))

IMG_SIZE = 224
BATCH = 16
BACKBONE = "efficientnet"
EPOCHS_FROZEN = 15
EPOCHS_FINETUNE = 10
N_CLASSES = len(MORPH_CLASSES)

# Split estratificado train/val/test
try:
    train_df, temp_df = train_test_split(
        df, test_size=0.30, stratify=df["label"], random_state=SEED)
    val_df, test_df = train_test_split(
        temp_df, test_size=0.50, stratify=temp_df["label"], random_state=SEED)
except ValueError as e:
    print(f"Advertencia: No se pudo realizar el split estratificado ({e}). Realizando split aleatorio simple.")
    train_df, temp_df = train_test_split(
        df, test_size=0.30, random_state=SEED)
    val_df, test_df = train_test_split(
        temp_df, test_size=0.50, random_state=SEED)

for name, d in [("Train", train_df), ("Val", val_df), ("Test", test_df)]:
    print(f"\n{name}: {len(d)} imágenes")
    print(d["morphology"].value_counts().reindex(MORPH_CLASSES).fillna(0).astype(int).to_dict())

# Pipelines tf.data + aumentos + pesos de clase
if BACKBONE == "efficientnet":
    preprocess = tf.keras.applications.efficientnet.preprocess_input
else:
    preprocess = tf.keras.applications.mobilenet_v3.preprocess_input

def load_image(path, label):
    img = tf.io.read_file(path)
    img = tf.image.decode_image(img, channels=3, expand_animations=False)
    img = tf.image.resize(img, [IMG_SIZE, IMG_SIZE])
    img = tf.cast(img, tf.float32)
    return img, label

# Aumentos
data_aug = tf.keras.Sequential([
    tf.keras.layers.RandomFlip("horizontal_and_vertical"),
    tf.keras.layers.RandomRotation(0.15),
    tf.keras.layers.RandomZoom(0.15),
    tf.keras.layers.RandomBrightness(0.2),
    tf.keras.layers.RandomContrast(0.2),
], name="aumentos")

def make_ds(d, training=False):
    ds = tf.data.Dataset.from_tensor_slices((d["path"].values, d["label"].values))
    if training:
        ds = ds.shuffle(len(d), seed=SEED)
    ds = ds.map(load_image, num_parallel_calls=tf.data.AUTOTUNE)
    if training:
        ds = ds.map(lambda x, y: (data_aug(x, training=True), y),
                    num_parallel_calls=tf.data.AUTOTUNE)
    ds = ds.map(lambda x, y: (preprocess(x), y), num_parallel_calls=tf.data.AUTOTUNE)
    return ds.batch(BATCH).prefetch(tf.data.AUTOTUNE)

train_ds = make_ds(train_df, True)
val_ds = make_ds(val_df)
test_ds = make_ds(test_df)

# Pesos de clase para desbalance
try:
    cw = compute_class_weight("balanced", classes=np.arange(N_CLASSES),
                              y=train_df["label"].values)
    class_weight = {i: w for i, w in enumerate(cw)}
except Exception as e:
    print(f"Advertencia: No se pudieron calcular pesos balanceados ({e}). Usando pesos uniformes.")
    class_weight = {i: 1.0 for i in range(N_CLASSES)}
print("Pesos de clase:", {MORPH_CLASSES[i]: round(w, 2) for i, w in class_weight.items()})

# Modelo (transfer learning)
if BACKBONE == "efficientnet":
    base = tf.keras.applications.EfficientNetB0(
        include_top=False, weights="imagenet", input_shape=(IMG_SIZE, IMG_SIZE, 3))
else:
    base = tf.keras.applications.MobileNetV3Small(
        include_top=False, weights="imagenet", input_shape=(IMG_SIZE, IMG_SIZE, 3))
base.trainable = False

inputs = tf.keras.Input((IMG_SIZE, IMG_SIZE, 3))
x = base(inputs, training=False)
x = tf.keras.layers.GlobalAveragePooling2D()(x)
x = tf.keras.layers.Dropout(0.3)(x)
outputs = tf.keras.layers.Dense(N_CLASSES, activation="softmax", name="morfologia")(x)
model = tf.keras.Model(inputs, outputs)

model.compile(optimizer=tf.keras.optimizers.Adam(1e-3),
              loss="sparse_categorical_crossentropy", metrics=["accuracy"])
model.summary()

# Entrenar cabeza congelada
print("\n--- Fase 1: Entrenando la cabeza con backbone congelado ---")
hist1 = model.fit(train_ds, validation_data=val_ds,
                  epochs=EPOCHS_FROZEN, class_weight=class_weight)

# Fine-tuning
print("\n--- Fase 2: Fine-tuning del modelo (descongelando últimas capas) ---")
base.trainable = True
for layer in base.layers[:-30]:
    layer.trainable = False

model.compile(optimizer=tf.keras.optimizers.Adam(1e-5),
              loss="sparse_categorical_crossentropy", metrics=["accuracy"])
hist2 = model.fit(train_ds, validation_data=val_ds,
                  epochs=EPOCHS_FINETUNE, class_weight=class_weight)

# Evaluación
print("\n--- Fase 3: Evaluación final en conjunto de Test ---")
y_true = np.concatenate([y.numpy() for _, y in test_ds])
y_prob = model.predict(test_ds)
y_pred = y_prob.argmax(axis=1)

print("\nReporte por clase (precision / recall / F1):\n")
print(classification_report(y_true, y_pred, target_names=MORPH_CLASSES,
                            labels=np.arange(N_CLASSES), zero_division=0))

cm = confusion_matrix(y_true, y_pred, labels=np.arange(N_CLASSES))
disp = ConfusionMatrixDisplay(cm, display_labels=MORPH_CLASSES)
disp.plot(xticks_rotation=45)
plt.title("Matriz de confusión - Morfología")
plt.tight_layout()

# Save matrix plot
plot_path = os.path.join(BASE_DIR, "confusion_matrix.png")
plt.savefig(plot_path)
print(f"Matriz de confusión guardada en: {plot_path}")

# Guardar modelos
model_keras_path = os.path.join(BASE_DIR, "seadd_morfologia.keras")
model_savedmodel_path = os.path.join(BASE_DIR, "seadd_morfologia_savedmodel")

model.save(model_keras_path)
model.export(model_savedmodel_path)
print(f"Modelo Keras guardado en: {model_keras_path}")
print(f"Modelo SavedModel exportado en: {model_savedmodel_path}")

def predecir_morfologia(image_path):
    img = tf.io.read_file(image_path)
    img = tf.image.decode_image(img, channels=3, expand_animations=False)
    img = tf.image.resize(img, [IMG_SIZE, IMG_SIZE])
    img = preprocess(tf.cast(img, tf.float32))[None, ...]
    p = model.predict(img, verbose=0)[0]
    i = int(p.argmax())
    return {"morfologia": MORPH_CLASSES[i], "confianza": float(p[i])}

if __name__ == "__main__":
    print("\nEntrenamiento completado exitosamente.")
