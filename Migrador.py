# Importando as bibliotecas
import sys
from PyQt5 import QtWidgets
from Funcoes.MessageBox import MessageBox
from ui_migrador import Ui_TelaPrincipal


class TelaMigrador(QtWidgets.QDialog):

    def __init__(self):
        super().__init__()

        self.ui = Ui_TelaPrincipal()
        self.ui.setupUi(self)

        self.setWindowTitle("Migrador de Repositórios - CAIXA")

        # Evento do botão
        self.ui.pushButton.clicked.connect(self.Btn_RDNG_Remocao_Links_click)

    def Btn_RDNG_Remocao_Links_click(self):
        print("Migração iniciada")


if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)

    tela = TelaMigrador()
    tela.show()

    sys.exit(app.exec_())