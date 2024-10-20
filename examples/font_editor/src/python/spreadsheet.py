import xml.etree.ElementTree as ET
from tkinter import Tk, Label, Entry, StringVar
from collections import defaultdict

class FormApp:
    def __init__(self, root, xml_root):
        self.root = root
        self.xml_root = xml_root
        self.fields = {}
        self.dependencies = defaultdict(list)

        # Create form fields based on XML
        for field in xml_root.findall('field'):
            field_id = field.get('id')
            label_text = field.get('label')
            expression = field.get('expression')

            Label(root, text=label_text).pack()
            var = StringVar()
            entry = Entry(root, textvariable=var)
            entry.pack()

            self.fields[field_id] = var

            # Record dependencies if this field has an expression
            if expression:
                for ref_id in self.get_referenced_ids(expression):
                    self.dependencies[ref_id].append(field_id)

            # Link changes to recompute expressions
            var.trace_add('write', self.update_expression)

    def get_referenced_ids(self, expression):
        """Extract referenced field IDs from an expression."""
        return [token for token in expression.split() if token in self.fields]

    def update_expression(self, *args):
        visited = set()

        # Update all fields with expressions, respecting dependency order
        for field_id in self.fields:
            self.evaluate_field(field_id, visited)

    def evaluate_field(self, field_id, visited):
        if field_id in visited:
            return
        visited.add(field_id)

        # Evaluate dependencies first
        for dependent_id in self.dependencies[field_id]:
            self.evaluate_field(dependent_id, visited)

        # Update the field if it has an expression
        field = self.xml_root.find(f".//field[@id='{field_id}']")
        expr = field.get('expression')
        if expr:
            try:
                value = eval(expr, {k: float(v.get() or 0) for k, v in self.fields.items()})
                self.fields[field_id].set(str(value))
            except Exception as e:
                pass  # Handle any evaluation errors gracefully

if __name__ == "__main__":
    # XML defined as a multi-line string
    form_config_xml = """
    <form>
        <field id="a" type="number" label="Value A"/>
        <field id="b" type="number" label="Value B"/>
        <field id="sum" type="number" label="Sum" expression="a + b"/>
        <field id="c" type="number" label="Value C"/>
        <field id="mul_sum" type="number" label="Mult Sum" expression="sum * c"/>
    </form>
    """

    # Parse the XML from the string
    root = ET.fromstring(form_config_xml)

    root_window = Tk()
    form_app = FormApp(root_window, root)
    root_window.mainloop()
