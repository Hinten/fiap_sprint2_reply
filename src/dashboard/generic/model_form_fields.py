from io import BytesIO

from src.database.dynamic_import import get_model_by_table_name
from src.database.tipos_base.model import Model
from typing import Any
from enum import Enum
import streamlit as st
from sqlalchemy import String, Text, Enum, Float, Boolean, Integer, DateTime, LargeBinary
from datetime import datetime
import logging
from typing import Optional
from PIL import Image


class ModelFormField:

    def __init__(self,
                 model: type[Model],
                 field_name: str,
                 label: Optional[str] = None,
                 nullable: bool or None = None
                 ):
        self.model = model
        self.field_name = field_name
        self.field = model.get_field(field_name)
        self.label = label or model.get_field_display_name(field_name)
        self.current_value = None
        self.nullable = nullable or self.field.nullable

    def render(self, initial_value=None, show_validation=False) -> Any:

        new_value = None

        if bool(self.field.foreign_keys):
            # pega todos os items da tabela relacionada e exibe um selectbox

            # Obter o nome da tabela relacionada
            table_name = list(self.field.foreign_keys)[0].column.table.name

            # Importar dinamicamente o modelo relacionado
            related_class = get_model_by_table_name(table_name)

            # Buscar todos os registros da tabela relacionada
            related_items = related_class.all()

            # Criar opções para o selectbox
            options = [(item.id, str(item)) for item in related_items]

            # Obter o valor atual

            # Exibir o selectbox
            _new_value = st.selectbox(
                label=self.label,
                options=options,
                format_func=lambda x: x[1],
                index=[opt[0] for opt in options].index(initial_value) if initial_value else None,
                help=self.field.comment,
            )

            if _new_value is not None:
                new_value = _new_value[0]
            else:
                new_value = None

        elif isinstance(self.field.type, Enum):

            options = [item.value for item in self.field.type.enum_class]

            index = options.index(initial_value) if initial_value in options else None

            new_value = st.selectbox(
                index=index,
                options=options,
                format_func=lambda x: str(self.field.type.enum_class(x)),
                label=self.label,
                help=self.field.comment,
                placeholder="Escolha uma opção",

            )

        elif isinstance(self.field.type, Float):
            # Exibir um campo de texto para editar o valor
            new_value = st.number_input(
                value=initial_value,
                label=self.label,
                help=self.field.comment,
                format="%.2f",
                step=0.01,
            )

        elif isinstance(self.field.type, Integer):
            # Exibir um campo de texto para editar o valor
            new_value = st.number_input(
                value=initial_value,
                label=self.label,
                help=self.field.comment,
                format="%d",
                step=1,
            )

        elif isinstance(self.field.type, Boolean):

            if self.field.nullable:
                options = ["Sim", "Não", "Indefinido"]
            else:
                options = ["Sim", "Não"]

            _valor = "Sim" if initial_value else "Não" if initial_value is not None else "Indefinido"

            index = options.index(_valor) if _valor in options else None

            new_value = st.selectbox(
                label=self.label,
                options=options,
                index=index,
                help=self.field.comment,
            )

        elif isinstance(self.field.type, DateTime):
            # Exibir um campo de data/hora para editar o valor
            date = st.date_input(
                label=f"{self.label} - Data",
                format="DD/MM/YYYY",
                value=initial_value,
                help=self.field.comment,
            )

            time = st.time_input(
                label=f"{self.label} - Hora",
                value=initial_value,
                help=self.field.comment,
            )

            if date is not None or time is not None:

                new_value = datetime.combine(date or datetime.now().date(), time or datetime.now().time())

            else:
                new_value = None

        elif isinstance(self.field.type, Text):
            # Exibir um campo de texto para editar o valor
            new_value = st.text_area(
                value=initial_value,
                label=self.label,
                help=self.field.comment,
                max_chars=self.field.type.length,
            )

        elif isinstance(self.field.type, String):
            # Exibir um campo de texto para editar o valor
            new_value = st.text_input(
                value=initial_value,
                label=self.label,
                help=self.field.comment,
                max_chars=self.field.type.length,
            )

        elif isinstance(self.field.type, LargeBinary):

            extensions = self.field.info.get('extensions', None)

            if initial_value:

                if extensions is not None and 'jpeg' in extensions:
                    imagem = Image.open(BytesIO(initial_value))
                    st.write(imagem)

                else:
                    st.write("Arquivo carregado, mas não é possível exibir o conteúdo.")


            uploaded_file = st.file_uploader(
                label=self.label,
                type=extensions,
                help=self.field.comment,
            )

            if uploaded_file is not None:
                new_value = uploaded_file.read()
            else:
                new_value = initial_value

        else:
            logging.warning(f"Tipo de campo não suportado: {self.field.type}")
            st.warning(f"Tipo de campo não suportado: {self.field.type}")
            print(self.field.type, type(self.field.type))
            raise NotImplementedError(f"Tipo de campo não suportado: {self.field.type}")

        if show_validation and self.validate(new_value, required=not self.nullable):
            st.warning(f"Valor inválido para o campo {self.label}: {self.validate(new_value)}")

        self.current_value = new_value

        return new_value

    def validate(self, value:Any, required:bool=True) -> str or None:
        if value is None and not required:
            print(f"Campo {self.label} não é obrigatório e o valor é None.")
            return None

        if value is None and required:
            print(f"Campo {self.label} é obrigatório e o valor é None.")
            return f"O campo {self.label} é obrigatório."

        return self.model.validate_field(self.field.name, value)

    def is_valid(self, value:Any, required:bool=True) -> bool:
        """
        Verifica se o valor é válido para o campo.
        :param value: Valor a ser validado.
        :param required: Se o campo é obrigatório.
        :return: True se o valor for válido, False caso contrário.
        """
        return self.validate(value, required) is None