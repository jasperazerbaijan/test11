# Copyright (C) 2017, 2018, 2019, 2020  alfred richardsn
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


new_request = (
    'Oyun yaradıldı.\n'
    'Oyun yaradıcısı: {owner}.\n'
    'Oyun silinmə vaxtı: {time} UTC.\n'
    '{order}'
)

take_card = (
    'Oyun başladı!\n\n'
    'Oyunçuların sırası belədir:\n'
    '{order}\n\n'
    '[{not_took}] Nömrəli oyunçular, gəlin kartları çıxartaq!!'
)

morning_message = (
    '{peaceful_night}'
    'Gün keçir {day}.\n'
    'Bu axşam kimə səs verəcəyinə qərar vermək üçün vaxtın var.\n'
    '──────────────────\n'
    'Oyunçular:\n'
    '{order}'
)

vote = (
    'Şəhər, səs verməyin vaxtı gəldi!\n'
    '{vote}'
)

gallows = (
    '<code>'
    '___________\n'
    '|         |\n'
    '|        %s\n'
    '|        %s\n'
    '|        %s\n'
    '|\n'
    '|'
    '</code>\n'
    '{result}\nSöz: {word}{attempts}{players}'
)
