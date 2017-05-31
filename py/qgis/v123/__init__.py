# -*- coding: utf-8 -*-
"""
/***************************************************************************
 v123
                                 A QGIS plugin
 v123
                             -------------------
        begin                : 2017-03-24
        copyright            : (C) 2017 by v123
        email                : v123@v123
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load v123 class from file v123.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .v123 import v123
    return v123(iface)
