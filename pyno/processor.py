from typing import Tuple

from .element import Element


class Processor():
    '''
    Processor is a engine of Pyno, 
    there functions defines and outputs calculates
    '''

    def init_processor(self, global_scope):
        self.proc_result = None

        self.call_func = None
        self.cleanup_func = None

        self.need_update = True
        self.problem = False
        self.problem_desc = ''

        self.local_scope = {}

    def reset_proc(self):
        self.proc_result = None

    def processor(self, connected_to, outputs):
        # Called every frame

        if self.proc_result and not self.need_update:
            return self.proc_result

        # check all in-connections, get results and gave names of in-puts
        gen_inputs = {}
        for connection in connected_to:
            try:
                inputs = connection['output']['node'].processor()
                data = inputs[connection['output']['put']['name']]
            except:
                self.problem = True
                self.problem_desc = 'Can\'t read input'
                continue
            gen_inputs[connection['input']['put']['name']] = data

        # run-time mode: just get inputs and put in function
        get_outputs = {}
        try:
            result = self.call_func(**gen_inputs)
        except Exception as ex:
            if not self.problem:
                self.problem_desc = "Runtime error: " + str(ex)
            self.problem = True
        else:
            if isinstance(result, Tuple) and len(outputs) > 1:
                for output in outputs:
                    item = result[outputs.index(output)]
                    get_outputs[output] = item  # tuple output
            else:
                get_outputs[outputs[0]] = result  # one output
            # build output
            self.proc_result = get_outputs
            self.problem = False

        return self.proc_result

    def cleanup(self):
        try:
            self.cleanup_func()
        except Exception as ex:
            if not self.problem:
                self.problem_desc = "Cleanup error: " + str(ex)
            self.problem = True
