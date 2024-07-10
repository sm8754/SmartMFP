import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox
import tkinter.simpledialog
from tkinter import simpledialog
from openai import OpenAI
import pycromanager
import os
from PIL import Image
import re
from Microscope.Tasks.LLM_CCA_Fast_Screening_4slides import VLT_CCA_Fast_Screening_4slides
from Microscope.Tasks.LLM_CCA_Class_Screening_4slides import VLT_CCA_Class_Screening_4slides
from Microscope.Tasks.LLM_HCC_seg import VLT_HCC_Seg_4slides
messages = []
client = OpenAI(api_key="")
client.models.list()

def Chat_init_images():
    role = 'system'
    with open('\Sub_Tasks.txt', encoding='utf-8') as f:
        one_content = f.read()

    one_content = 'developer：' + one_content
    one_answer, messages_list = send_to_chatgpt_and_return_the_reply(role, one_content)
    return one_answer, messages_list

def Chat_init_analysis():
    role = 'system'
    with open('\Analysis.txt', encoding='utf-8') as f:
        one_content = f.read()

    one_content = 'developer：' + one_content
    one_answer, messages_list = send_to_chatgpt_and_return_the_reply(role, one_content)
    return one_answer, messages_list

def send_to_chatgpt_and_return_the_reply(role, content):

    messages.append({"role": role, "content": content})

    chat_response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )

    answer = chat_response.choices[0].message.content
    messages.append({"role": "assistant", "content": answer})

    return answer, messages

def extract_score(text):
    match = re.search(r'(\d+) out of 10', text)
    if match:
        return float(match.group(1))
    return 0.0


def get_similarity(text1, text2):
    prompt_message = {
        'role': 'system',
        'content': 'You are a helpful assistant. Compare the similarity between the following texts and rate it from 0 to 10.'
    }
    message1 = {'role': 'user', 'content': text1}
    message2 = {'role': 'user', 'content': text2}

    response = client.chat.completions.create(
      model="gpt-4o",
      messages=[prompt_message, message1, message2]
    )
    content = response.choices[0].message['content']
    return extract_score(content)

def user_chat(content):

    role = 'user'
    one_content = 'Doctor：' + content
    one_answer, messages_list = send_to_chatgpt_and_return_the_reply(role, one_content)
    return one_answer, messages_list

def Completion_prompt(run_result):

    role = 'system'
    one_content = 'O7975K'
    one_answer, messages_list = send_to_chatgpt_and_return_the_reply(role, one_content)
    return one_answer, messages_list

def open_application(self):

    keys = []
    app_commands = {
        "SCR": "LLM_CCA_Fast_Screening_4slides.py",
        "CLS": "CCA_Class_Screening_4slides.py",
        "SEG": "VLT_HCC_Seg_4slides.py",
        "IMAGE AQU": "Sub_tasks.py",
        # more code
    }

    for key in app_commands.keys():
        keys.append(key)

    if self.code_match:
        os.system('python ' + app_commands["IMAGE AQU"])
        return 'O7975K'

    elif ("fast" in self.analysis_results) or ("fast screening" in self.analysis_results):
        results = VLT_CCA_Fast_Screening_4slides()
        return 'O7975K. ' + results

    elif (("classification" in self.analysis_results) or ("grade" in self.analysis_results)
           or ('detail' in self.analysis_results) or ('careful' in self.analysis_results)\
            or ('analysis' in self.analysis_results)):
        results = VLT_CCA_Class_Screening_4slides()
        return 'O7975K. ' + results
    elif (("Segmentation" in self.analysis_results) or ("liver cancer segmentation" in self.analysis_results)
           or ('tumor segmentation' in self.analysis_results)):
        results = VLT_HCC_Seg_4slides()
        return 'O7975K. ' + results


class OptionDialog(simpledialog.Dialog):
    def body(self, master):
        tk.Label(master, text="Please select:").grid(row=0)
        self.var = tk.StringVar()
        self.var.set(None)
        choices = ["Language Guided Image Acquisition", "Language Guided Pathological Analysis"]
        for i, choice in enumerate(choices):
            tk.Radiobutton(master, text=choice, variable=self.var, value=choice).grid(row=i+1, sticky=tk.W)
        return

    def apply(self):
        self.result = self.var.get()


class InteractiveGUI:
    PAD_X = 20
    PAD_Y = 10

    def __init__(self, root):
        self.root = root
        self.root.title("VLT-OM")
        self.initialize()

    def initialize(self):
        self.debug_mode_var = tk.BooleanVar()
        self.debug_mode_var.set(False)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        self.root.rowconfigure(2, weight=1)

        self.top_frame = ttk.LabelFrame(self.root, text="Status bar")
        self.top_frame.grid(row=0, column=0, padx=self.PAD_X, pady=self.PAD_Y, sticky='ew')
        self.top_frame.columnconfigure(1, weight=1)

        self.status_label = ttk.Label(self.top_frame, text="Waiting to start")
        self.status_label.grid(row=0, column=0, padx=self.PAD_X, pady=self.PAD_Y, sticky='w')

        self.progress_bar = ttk.Progressbar(self.top_frame, mode="determinate")
        self.progress_bar.grid(row=0, column=1, padx=self.PAD_X, pady=self.PAD_Y, sticky='ew')

        # self.timer_label = ttk.Label(self.top_frame, text="Timer：0.0s")
        # self.timer_label.grid(row=0, column=2, padx=self.PAD_X, pady=self.PAD_Y, sticky='w')

        self.input_text = scrolledtext.ScrolledText(self.root, height=8)
        self.input_text.grid(row=1, column=0, padx=self.PAD_X, pady=self.PAD_Y, sticky='nsew')

        self.output_text = scrolledtext.ScrolledText(self.root, height=10)
        self.output_text.grid(row=2, column=0, padx=self.PAD_X, pady=self.PAD_Y, sticky='nsew')

        self.button_frame = ttk.LabelFrame(self.root, text="Operation")
        self.button_frame.grid(row=3, column=0, padx=self.PAD_X, pady=self.PAD_Y, sticky='ew')
        self.button_frame.columnconfigure(0, weight=1)

        # Create an inner frame to center the buttons within the button_frame
        self.inner_button_frame = tk.Frame(self.button_frame)
        self.inner_button_frame.grid(row=0, column=0, sticky='ew')

        # Assuming you have 5 buttons, you can manage the layout as follows:
        self.initialize_button = tk.Button(self.inner_button_frame, text="Initialization", command=self.initialize_process,
                                           width=20)
        self.initialize_button.pack(side=tk.LEFT, padx=self.PAD_X, pady=self.PAD_Y)

        self.voice_input_button = tk.Button(self.inner_button_frame, text="Voice Input", command=self.voice_input,
                                            state="disabled", width=20)
        self.voice_input_button.pack(side=tk.LEFT, padx=self.PAD_X, pady=self.PAD_Y)

        self.text_input_button = tk.Button(self.inner_button_frame, text="Text Input", command=self.text_input,
                                           state="disabled", width=20)
        self.text_input_button.pack(side=tk.LEFT, padx=self.PAD_X, pady=self.PAD_Y)

        self.finish_input_button = tk.Button(self.inner_button_frame, text="Input Completed", command=self.finish_input,
                                             state="disabled", width=20)
        self.finish_input_button.pack(side=tk.LEFT, padx=self.PAD_X, pady=self.PAD_Y)

        self.execute_button = tk.Button(self.inner_button_frame, text="Executing", command=self.execute_function,
                                        state="disabled", width=20)
        self.execute_button.pack(side=tk.LEFT, padx=self.PAD_X, pady=self.PAD_Y)

        # Add a new row for additional buttons
        self.inner_button_frame_2 = tk.Frame(self.button_frame)
        self.inner_button_frame_2.grid(row=1, column=0, sticky='ew')

        self.clear_input_button = tk.Button(self.inner_button_frame_2, text="Clear input field", command=self.clear_input,
                                            width=20)
        self.clear_input_button.pack(side=tk.LEFT, padx=self.PAD_X, pady=self.PAD_Y)

        self.clear_all_button = tk.Button(self.inner_button_frame_2, text="Clear All", command=self.clear_all, width=20)
        self.clear_all_button.pack(side=tk.LEFT, padx=self.PAD_X, pady=self.PAD_Y)

        self.end_session_button = tk.Button(self.button_frame, text="End session", command=self.confirm_end_session,
                                            state="disabled", width=20, bg='salmon', font=('Arial', 12, 'bold'))
        self.end_session_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

        # Debug Mode Checkbox at the bottom
        self.debug_mode_checkbox = ttk.Checkbutton(self.root, text="Debugging mode", variable=self.debug_mode_var)
        self.debug_mode_checkbox.grid(row=4, column=0, padx=self.PAD_X, pady=self.PAD_Y, sticky='ew')

        self.button_frame.grid_columnconfigure(0, weight=1)


    def show_option_dialog(self):
        options = ["Language Guided Image Acquisition", "Language Guided Pathological Analysis"]
        choice = simpledialog.askstring("Choose an option", "Please select:", choices=options)
        return choice

    def initialize_process(self):

        dialog = OptionDialog(self.root)
        choice = dialog.result

        if choice == "Language Guided Image Acquisition":
            identifier = "image_guidance"
        elif choice == "Language Guided Pathological Analysis":
            identifier = "custom_image_analysis"

        self.set_status("Initializing ...")
        self.progress_bar['value'] = 20
        self.voice_input_button['state'] = "disabled"
        self.text_input_button['state'] = "disabled"
        self.end_session_button['state'] = "disabled"
        self.root.update()

        self.set_status("Waiting to start ...")
        self.progress_bar['value'] = 100
        self.voice_input_button['state'] = "active"
        self.text_input_button['state'] = "active"
        self.end_session_button['state'] = "active"
        # self.timer_label.config(text="Timer：0.0s")
        self.initialize_button['state'] = "disabled"

    def voice_input(self):
        self.set_status("Voice inputting")
        self.voice_input_button['state'] = "disabled"
        self.text_input_button['state'] = "active"
        self.finish_input_button['state'] = "active"
        self.clear_input()
        self.clear_output()

    def text_input(self):
        self.set_status("Text inputting")
        self.text_input_button['state'] = "disabled"
        self.voice_input_button['state'] = "active"
        self.finish_input_button['state'] = "active"
        self.clear_input()
        self.clear_output()

    def finish_input(self):
        user_input = self.get_user_input()
        if user_input:
            self.set_status("Parsing your instructions")
            self.finish_input_button['state'] = "disabled"

            self.analysis_results, self.messages_list = user_chat(user_input)
            result = "VLT-OM：" + self.analysis_results

            self.output_text.insert(tk.END, "Doctor：" + user_input + "\n")
            self.set_status("Executing instructions...")

            # self.check_for_new_content()
            if "我相信我能够胜任" or 'I believe I can handle it' in self.analysis_results:
                self.execute_button['state'] = "active"

            self.code_match = re.search(r'```python(.*?)```', self.analysis_results, re.DOTALL)
            print(self.code_match)
            if self.code_match:
                extracted_code = self.code_match.group(1).strip()
                self.execute_button['state'] = "active"

                with open('E:\\LLM-Micro-main\\Microscope\\Tasks\\Sub_tasks.py', 'r', encoding='utf-8') as file:
                    lines = file.readlines()
                lines.insert(199, extracted_code + '\n')

                with open('E:\\LLM-Micro-main\\Microscope\\Tasks\\Sub_tasks.py', 'w', encoding='utf-8') as file:
                    file.writelines(lines)
            if self.code_match:
                respo_match = re.search(r'python\n(.*?)', result, re.DOTALL)
                extracted_respo = respo_match.group(1).strip()
                self.output_text.insert(tk.END, "--" + extracted_respo + "\n")
            else:
                self.output_text.insert(tk.END, "--" + result + "\n")

            self.set_status("Dialogue mode")
            self.finish_input_button['state'] = "active"

            self.dialog_operation()
            return self.analysis_results

    def disable_all_buttons(self):
        self.initialize_button.config(state=tk.DISABLED)
        self.voice_input_button.config(state=tk.DISABLED)
        self.text_input_button.config(state=tk.DISABLED)
        self.finish_input_button.config(state=tk.DISABLED)
        self.execute_button.config(state=tk.DISABLED)
        self.clear_input_button.config(state=tk.DISABLED)
        self.clear_all_button.config(state=tk.DISABLED)
        self.debug_mode_checkbox.config(state=tk.DISABLED)
        self.end_session_button.config(state=tk.DISABLED)

    def enable_all_buttons(self):
        self.initialize_button.config(state=tk.NORMAL)
        self.voice_input_button.config(state=tk.NORMAL)
        self.text_input_button.config(state=tk.NORMAL)
        self.finish_input_button.config(state=tk.NORMAL)
        self.execute_button.config(state=tk.NORMAL)
        self.clear_input_button.config(state=tk.NORMAL)
        self.clear_all_button.config(state=tk.NORMAL)
        self.debug_mode_checkbox.config(state=tk.NORMAL)
        self.end_session_button.config(state=tk.NORMAL)

    def check_thread(self, thread):
        if thread.is_alive():
            self.root.after(100, self.check_thread, thread)
        else:
            self.enable_all_buttons()

    def dialog_operation(self):
        user_input = self.get_user_input()


    def execute_function(self):
        run_result = open_application(self)

        self.set_status("Executing, please wait for completion before attempting again!")
        if self.code_match:
            with open('\\Sub_tasks.py', 'r', encoding='utf-8') as file:
                lines = file.readlines()

            del lines[199:]

            with open('\\Sub_tasks.py', 'w', encoding='utf-8') as file:
                file.writelines(lines)
        self.execute_button['state'] = "disabled"
        self.set_status("c")
        analysis_results, messages_list = Completion_prompt(run_result)
        result = "VLT-OM：" + analysis_results
        self.code_match = False
        self.output_text.insert(tk.END, "\n")
        self.output_text.insert(tk.END, "--" + result + "\n")


    def get_output_text(self):

        output_text = self.output_text.get("1.0", tk.END)
        return output_text

    def get_user_input(self):
        return self.input_text.get("1.0", "end-1c")

    def clear_input(self):
        self.input_text.delete(1.0, tk.END)

    def clear_output(self):
        self.output_text.delete(1.0, tk.END)

    def clear_all(self):
        self.clear_input()
        self.clear_output()
        self.set_status("Waiting to start")
        self.timer_label.config(text="Timer：0.0s")

    def set_status(self, status):
        self.status = status
        self.status_label.config(text=status)

    def toggle_debug_mode(self):
        if self.debug_mode_var.get():
            self.set_status("Debug mode enabled")
        else:
            self.set_status("Waiting to start")

        self.dialog_operation()

    def confirm_end_session(self):
        result = tkinter.messagebox.askokcancel("Confirm?", "End the conversation?")
        if result:
            self.root.destroy()

if __name__ == "__main__":

    root = tk.Tk()
    app_tkinter = InteractiveGUI(root)
    root.mainloop()
    # sys.exit(app.exec_())
