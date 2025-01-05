Metadata API
==========================

*mmodel* provides a metadata API to fully customize the ``__str__`` output
of the node, graph, model, and modelgroup object outputs.

Here is an example to define a custom formatter for the node object:


.. code-block:: python

    from mmodel.metadata import MetaDataFormatter, wrapper80
    from mmodel import Node

    nodeformatter = MetaDataFormatter(
        formatter_dict={
            "name": format_value,
            "node_func": format_func,
            "output": lambda key, value: [f"return: {value}"],
            "doc": format_shortdocstring,
        },
        meta_order=["name", "_", "node_func", "output", "_", "doc"],
        text_wrapper=wrapper80,
        shorten_list=["doc"],
        shorten_placeholder="...",
    )

The ``MetaDataFormatter`` class takes several parameters.

- ``formatter_dict``: a dictionary specifies the formatter function for each metadata key.
- ``meta_order``: a list specifies the order of the metadata keys. "_" is used to add a blank line.
- ``text_wrapper``: a textwrapper class that is used to wrap the text to desired width for the whole
- ``shorten_list``: a list of metadata keys that should be shortened if the text is too long.
  The shortening is done by the ``text_wrapper``.
- ``shorten_placeholder``: a string that is used to replace the shortened text.

The formatter function is defined to with "key" and "value" arguments, and returns a list of strings
that will be format to lines. The "key" is the metadata key,
and the value is the content of the metadata. If the key is in meta_order, but the formatter function
is not defined, the value of the key will be used as the string representation.

An example of the formatter function is shown below:

.. code-block:: python

    def format_list(key, value):
        """Format the metadata value that is a list."""

        if not value:
            return []
        elements = [f"\t- {v}" for v in value]
        return [f"{key}:"] + elements

In this function format the list content with a tab and a hyphen. If the value is empty,
then the metadata is not included in the output.

The formatter can be directly applied to a node object, or a custom node
class can be defined:

.. code-block:: python

    class CustomNode(Node):
        def __str__(self):
            return nodeformatter(self)

.. autosummary::

    mmodel.metadata.MetaDataFormatter

See :doc:`ref_metadata` for the full list of metadata formatter functions.
