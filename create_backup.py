import shutil
import os
import datetime

def create_backup():
    # Caminho do projeto (diretório atual)
    project_dir = os.getcwd()
    
    # Nome do arquivo de backup com timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"Backup_Emissor_Notas_Hube_{timestamp}"
    backup_path = os.path.join(project_dir, backup_filename)
    
    # Função para ignorar pastas/arquivos indesejados
    def ignore_patterns(path, names):
        ignored = []
        for name in names:
            if name in ['venv', '.git', '__pycache__', '.streamlit', 'dist', 'build']:
                ignored.append(name)
            elif name.endswith('.zip') or name.endswith('.rar'):
                ignored.append(name)
        return ignored

    print(f"Iniciando backup de: {project_dir}")
    print(f"Criando arquivo: {backup_filename}.zip ...")

    try:
        shutil.make_archive(backup_path, 'zip', project_dir)
        print(f"✅ Backup concluído com sucesso: {backup_filename}.zip")
    except Exception as e:
        print(f"❌ Erro ao criar backup: {e}")

if __name__ == "__main__":
    create_backup()
