from textual.containers import Horizontal, Container, VerticalScroll
from textual.widgets import Header, Footer, Label, Input, Switch, RadioSet, RadioButton, Button


class MainUI(VerticalScroll):
	def compose(self):
		yield Header(show_clock=True)
		yield Footer()

		with Container():
			yield Label("Enter input file name:", shrink=True)
			yield Input(id="input_file", placeholder="File name with extension")

		with Horizontal():
			with Container():
				yield Label("Enter output file name:", shrink=True)
				yield Input(id="output_file", placeholder="File name with extension")

			with Container(classes="switch_container"):
				yield Label("Overwrite:", shrink=True)
				yield Switch(id="overwrite_mode", animate=False)

		with Horizontal():
			with Container(classes="switch_container"):
				yield Label("Mute:", shrink=True)
				yield Switch(id="mute_mode", animate=False)

			with Container():
				yield Label("Loop:", shrink=True)
				yield Input(id="loop_input", placeholder="Number only (0 - 10)", value="0")

			with Container(classes="switch_container"):
				yield Label("Debug Mode:", shrink=True)
				yield Switch(id="debug_mode", animate=False)

		with Container():
			yield Label("Threads:", shrink=True)
			yield Input(id="threads_value", placeholder=f"Number only (0 - {self.app.MAX_THREADS})", value="0")

		with Container(id="thread_type_container"):
			yield Label("Thread Type:", shrink=True)
			with RadioSet(id="thread_type"):
				yield RadioButton("AUTO", value="AUTO", id="thread_auto")
				yield RadioButton("FRAME", value="FRAME", id="thread_frame")
				yield RadioButton("SLICE", value="SLICE", id="thread_slice")

		with Horizontal():
			with Container():
				yield Label("Codec:", shrink=True)
				with RadioSet(id="codec_input"):
					yield Label("Write your output file name with extension first", classes="info", shrink=True)

			with Container():
				yield Label("Format:", shrink=True)
				with RadioSet(id="sample_fmt"):
					yield Label("Select a Codec first", classes="info", shrink=True)

		with Horizontal():
			with Container():
				yield Label("Bitrate:", shrink=True)
				yield Input(id="bitrate", placeholder="Select a Codec first", disabled=True)

			with Container(classes="video_container"):
				yield Label("Frame Rate:", shrink=True)
				yield Input(id="frame_rate", placeholder="Number only (24 - 120)", value="30")

		with Container(id="audio_container"):
			yield Label("Sample Rate:", shrink=True)
			with RadioSet(id="sample_rate"):
				yield Label("Select a Codec first", classes="info", shrink=True)

		with Horizontal(classes="video_container"):
			with Container():
				yield Label("Width:", shrink=True)
				yield Input(id="res_width", placeholder="Number only (800 - 1920)")

			with Container():
				yield Label("height:", shrink=True)
				yield Input(id="res_height", placeholder="Number only (600 - 1080)")

		with Container(id="cpp_container"):
			with Container():
				yield Label("CRF:", shrink=True)
				yield Input(id="crf", placeholder="Number only (5 - 50)")

			with Horizontal():
				with Container():
					yield Label("Profile", shrink=True)
					with RadioSet(id="profile"):
						yield RadioButton("High", value=True)
						yield RadioButton("Main")
						yield RadioButton("Baseline")

				with Container():
					yield Label("Preset", shrink=True)
					with RadioSet(id="preset"):
						yield RadioButton("Very Slow")
						yield RadioButton("Slower")
						yield RadioButton("Slow")
						yield RadioButton("Medium")
						yield RadioButton("Fast", value=True)
						yield RadioButton("Faster")
						yield RadioButton("Very Fast")
						yield RadioButton("Super Fast")
						yield RadioButton("Ultra Fast")

				with Container(id="cppt_container"):
					yield Label("Tune", shrink=True)
					with RadioSet(id="tune"):
						yield RadioButton("Zero Latency", value=True)
						yield RadioButton("Animation")
						yield RadioButton("Fast Decode")
						yield RadioButton("Film")
						yield RadioButton("Grain")
						yield RadioButton("Still Image")

		with Container(id="button_container"):
			yield Button("Submit", id="submit_btn", variant="primary")
