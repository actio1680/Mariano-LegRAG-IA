# ============================================================
# Mariano LegRAG IA - Gestor de índice y estado
# ============================================================
import os
import shutil
import hashlib
import json


class GestorIndice:
    def __init__(self, carpeta_pdfs="pdfs", carpeta_indice="vectorstore/db_faiss"):
        self.carpeta_pdfs = carpeta_pdfs
        self.carpeta_indice = carpeta_indice
        self.archivo_estado = "estado_documentos.json"

    # --------------------------------------------------------
    # Hashes por archivo
    # --------------------------------------------------------
    def _hash_archivo(self, ruta_pdf):
        hasher = hashlib.md5()
        hasher.update(os.path.basename(ruta_pdf).encode())
        hasher.update(str(os.path.getmtime(ruta_pdf)).encode())
        return hasher.hexdigest()

    def ya_indexado(self, ruta_pdf):
        if not os.path.exists(self.archivo_estado):
            return False
        with open(self.archivo_estado, 'r') as f:
            estado = json.load(f)
        nombre = os.path.basename(ruta_pdf)
        hash_guardado = estado.get('archivos', {}).get(nombre)
        if hash_guardado is None:
            return False
        return hash_guardado == self._hash_archivo(ruta_pdf)

    # --------------------------------------------------------
    # Estado persistente
    # --------------------------------------------------------
    def guardar_estado(self):
        archivos = {}
        if os.path.exists(self.carpeta_pdfs):
            for pdf in os.listdir(self.carpeta_pdfs):
                if pdf.endswith('.pdf'):
                    ruta = os.path.join(self.carpeta_pdfs, pdf)
                    archivos[pdf] = self._hash_archivo(ruta)

        estado = {
            'ultima_actualizacion': (
                str(os.path.getmtime(self.carpeta_indice))
                if os.path.exists(self.carpeta_indice)
                else ""
            ),
            'pdfs': sorted(archivos.keys()),
            'archivos': archivos,
        }
        with open(self.archivo_estado, 'w') as f:
            json.dump(estado, f, indent=2)

    def pdfs_registrados(self):
        if not os.path.exists(self.archivo_estado):
            return []
        with open(self.archivo_estado, 'r') as f:
            estado = json.load(f)
        return sorted(estado.get('archivos', {}).keys())

    def pdfs_huerfanos(self, pdfs_en_disco):
        registrados = set(self.pdfs_registrados())
        return sorted(registrados - set(pdfs_en_disco))

    # --------------------------------------------------------
    # Limpieza - Elimina el índice, el estado y archivos sueltos
    # --------------------------------------------------------
    def limpiar_indice(self):
        if os.path.exists(self.carpeta_indice):
            shutil.rmtree(self.carpeta_indice)
        if os.path.exists(self.archivo_estado):
            os.remove(self.archivo_estado)
        for archivo in os.listdir('.'):
            if archivo.endswith('.pkl') or archivo.endswith('.faiss'):
                try:
                    os.remove(archivo)
                except OSError:
                    pass

    # --------------------------------------------------------
    # Debug - Muestra el estado actual por consola
    # --------------------------------------------------------
    def mostrar_estado(self):
        print("\n=== ESTADO DEL GESTOR ===")
        print(f"Carpeta PDFs: {self.carpeta_pdfs}")
        print(f"Carpeta índice: {self.carpeta_indice}")

        if os.path.exists(self.carpeta_pdfs):
            pdfs = [f for f in os.listdir(self.carpeta_pdfs) if f.endswith('.pdf')]
            print(f"PDFs encontrados: {pdfs}")
        else:
            print(f"❌ Carpeta {self.carpeta_pdfs} no existe")

        if os.path.exists(self.archivo_estado):
            with open(self.archivo_estado, 'r') as f:
                estado = json.load(f)
            print(f"PDFs registrados: {estado.get('pdfs', [])}")
        else:
            print("No hay estado guardado")

        print("=" * 30 + "\n")