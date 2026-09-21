"""Recolha automática de cotações.

Cada collector consulta apenas fontes públicas (sem login) e **nunca inventa
dados**: se um montante não conseguir ser obtido, é omitido; se nenhum montante
for válido, o collector falha (CollectorError) e nenhuma ronda é registada.
"""