import os

from attr.validators import disabled
from textual.app import App, ComposeResult, on
from textual.containers import Horizontal, Container, VerticalScroll
from textual.widgets import Footer, Header, Input, Label, Checkbox, RadioSet, RadioButton, Button, Switch
from textual_slider import Slider

from simplemp.simplemp import transcode
from simplemp.validator import codec_dict, audio_sample_fmt_dict, pixel_fmt_dict, check_audio_codec, samplerate_range_dict, bitrate_range_dict

from functions.intInputValidator import int_input_validator
from functions.stringToInt import to_int


class SimpleMP(App):
	CSS_PATH = "styles.tcss"
	MAX_THREADS = os.cpu_count()

	@staticmethod
	def compose() -> ComposeResult:
		with VerticalScroll():
			yield Header(show_clock=True)
			yield Footer()

			with Container():
				yield Label("Enter input file name:", shrink=True)
				yield Input(id="input_file", placeholder="File name with extension...")

			with Horizontal():
				with Container():
					yield Label("Enter output file name:", shrink=True)
					yield Input(id="output_file", placeholder="File name with extension...")

				with Container(classes="switch_container"):
					yield Label("Overwrite:", shrink=True)
					yield Switch(id="overwrite_mode", animate=False)

			with Horizontal():
				with Container(classes="switch_container"):
					yield Label("Mute:", shrink=True)
					yield Switch(id="mute_mode", animate=False)

				with Container():
					yield Label("Loop:", shrink=True)
					yield Input(id="loop_input", placeholder="Number only (0 - 10)...", value="0")

				with Container(classes="switch_container"):
					yield Label("Debug Mode:", shrink=True)
					yield Switch(id="debug_mode", animate=False)

			with Horizontal():
				with Container():
					yield Label("Threads:", shrink=True)
					yield Input(id="threads_value", placeholder=f"Number only (0 - {SimpleMP.MAX_THREADS})...",
					            value="0")

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
						yield Label("Write your output file name with extension first...", classes="info", shrink=True)

				with Container():
					yield Label("Format:", shrink=True)
					with RadioSet(id="sample_fmt"):
						yield Label("Select a Codec first...", classes="info", shrink=True)

			with Horizontal(id="audio_container"):
				with Container():
					yield Label("Sample Rate:", shrink=True)
					with RadioSet(id="sample_rate"):
						yield Label("Select a Codec first...", classes="info", shrink=True)

				with Container():
					yield Label("Bitrate:", shrink=True)
					yield Input(id="bitrate", placeholder="Select a Codec first...", disabled=True)

			with Container(id="button_container"):
				yield Button("Submit", id="submit_btn", variant="primary")

	@on(Input.Changed)
	def on_input_changed(self, event: Input.Changed) -> None:
		if event.input.id == "output_file":
			filename = event.input.value
			ext = ""
			if '.' in filename:
				for c in filename[::-1]:
					if c == '.':
						break
					ext += c
				ext = "." + ext[::-1].lower()
			self.update_codec_set(ext)

		elif event.input.id == "threads_value":
			event.input.value = int_input_validator(event.input.value, self.MAX_THREADS, 0)

		elif event.input.id == "loop_input":
			event.input.value = int_input_validator(event.input.value, 10, 0)

		elif event.input.id == "bitrate":
			codec_input = self.query_one("#codec_input", RadioSet)
			selected_codec = codec_input.pressed_button.label if codec_input.pressed_button else None
			if selected_codec and selected_codec in bitrate_range_dict:
				min_bitrate, max_bitrate = bitrate_range_dict[selected_codec]
				event.input.value = int_input_validator(event.input.value, max_bitrate, min_bitrate)

	@on(Switch.Changed, "#overwrite_mode")
	def handle_overwrite_toggle(self, event: Switch.Changed):
		input_file = self.query_one("#input_file", Input)
		output_file = self.query_one("#output_file", Input)

		if event.value:
			output_file.value = input_file.value
			output_file.disabled = True
		else:
			output_file.disabled = False

	def update_codec_set(self, ext: str):
		codec_input = self.query_one("#codec_input", RadioSet)
		sample_fmt = self.query_one("#sample_fmt", RadioSet)
		sample_rate = self.query_one("#sample_rate", RadioSet)
		bitrate_input = self.query_one("#bitrate", Input)

		codec_input.value = None
		codec_input.remove_children()

		sample_fmt.value = None
		sample_fmt.remove_children()

		sample_rate.value = None
		sample_rate.remove_children()

		bitrate_input.disabled = True
		bitrate_input.placeholder = "Select a Codec first..."
		bitrate_input.value = ""

		if ext in codec_dict:
			codecs = codec_dict[ext]
			if not codecs:
				codec_input.mount(Label("No codecs available.", shrink=True))
				sample_fmt.mount(Label("Select a Codec first...", shrink=True))
				sample_rate.mount(Label("Select a Codec first...", shrink=True))
				bitrate_input.disabled = True
				bitrate_input.placeholder = "Select a Codec first..."
				bitrate_input.value = ""
				return
		else:
			codec_input.mount(Label("No codecs available.", shrink=True))
			sample_fmt.mount(Label("Select a Codec first...", shrink=True))
			sample_rate.mount(Label("Select a Codec first...", shrink=True))
			bitrate_input.disabled = True
			bitrate_input.placeholder = "Select a Codec first..."
			bitrate_input.value = ""
			return

		for codec in codecs:
			codec_input.mount(RadioButton(codec))

		sample_fmt.mount(Label("Select a Codec first...", shrink=True))
		sample_rate.mount(Label("Select a Codec first...", shrink=True))
		bitrate_input.disabled = True
		bitrate_input.placeholder = "Select a Codec first..."
		bitrate_input.value = ""

	@on(RadioSet.Changed, "#codec_input")
	def codec_changed(self, event: RadioSet.Changed):
		selected_button = event.pressed
		selected_codec = selected_button.label
		self.update_fmt_set(str(selected_codec))
		self.update_sample_rate_set(str(selected_codec))
		self.update_bitrate_range(str(selected_codec))

		if check_audio_codec(selected_codec):
			self.query_one("#audio_container", Horizontal).styles.display = "block"
		else:
			self.query_one("#audio_container", Horizontal).styles.display = "none"

	def update_fmt_set(self, selected_codec: str):
		fmt_set = self.query_one("#sample_fmt", RadioSet)
		fmt_set.value = None
		fmt_set.remove_children()

		sample_fmt_dict = pixel_fmt_dict | audio_sample_fmt_dict

		if selected_codec in sample_fmt_dict:
			fmts = sample_fmt_dict[selected_codec]
			if not fmts:
				fmt_set.mount(Label("No format available.", shrink=True))
				return
		else:
			fmt_set.mount(Label("No format available.", shrink=True))
			return

		for fmt in fmts:
			fmt_set.mount(RadioButton(fmt))

	def update_sample_rate_set(self, selected_codec: str):
		sample_rate_set = self.query_one("#sample_rate", RadioSet)
		sample_rate_set.value = None
		sample_rate_set.remove_children()

		if selected_codec in samplerate_range_dict:
			sp_rates = samplerate_range_dict[selected_codec]
			if not sp_rates:
				sample_rate_set.mount(Label("No rate available.", shrink=True))
				return
		else:
			sample_rate_set.mount(Label("No rate available.", shrink=True))
			return

		for sp_rate in sp_rates:
			sample_rate_set.mount(RadioButton(str(sp_rate)))

	def update_bitrate_range(self, selected_codec: str):
		bitrate_input = self.query_one("#bitrate", Input)
		bitrate_input.disabled = False
		bitrate_input.value = ""

		if selected_codec in bitrate_range_dict:
			min_bitrate, max_bitrate = bitrate_range_dict[selected_codec]
			bitrate_input.placeholder = f"Number only ({min_bitrate} - {max_bitrate})..."

		else:
			bitrate_input.disabled = True
			bitrate_input.placeholder = "No bitrate available..."
			bitrate_input.value = ""

	@on(Button.Pressed, "#submit_btn")
	def on_submit(self):
		input_file = self.query_one("#input_file", Input).value
		output_file = self.query_one("#output_file", Input).value
		overwrite_mode = self.query_one("#overwrite_mode", Switch).value
		mute_mode = self.query_one("#mute_mode", Switch).value
		loop = self.query_one("#loop_input", Input).value
		debug_mode = self.query_one("#debug_mode", Switch).value
		threads_value = self.query_one("#threads_value", Input).value
		thread_type = self.query_one("#thread_type", RadioSet).pressed_button.label if self.query_one("#thread_type", RadioSet).pressed_button else None
		codec_input = self.query_one("#codec_input", RadioSet).pressed_button.label if self.query_one("#codec_input", RadioSet).pressed_button else None
		sample_fmt = self.query_one("#sample_fmt", RadioSet).pressed_button.label if self.query_one("#sample_fmt", RadioSet).pressed_button else None
		sample_rate = self.query_one("#sample_rate", RadioSet).pressed_button.label if self.query_one("#sample_rate", RadioSet).pressed_button else None
		bitrate = self.query_one("#bitrate", Input).value

		# if not input_file or not output_file:
		# 	return self.notify("Input and output file are required!", severity="error")
		# if not codec_input:
		# 	return self.notify("Select a codec!", severity="error")

		if check_audio_codec(codec_input):
			transcode(
				input_file=input_file,
				output_file=output_file,
				overwrite=overwrite_mode,
				mute=mute_mode,
				loop=to_int(loop),
				debug=debug_mode,
				thread_count=to_int(threads_value),
				thread_type=str(thread_type),
				audio_encoder=str(codec_input),
				sample_fmt=str(sample_fmt),
				samplerate=to_int(str(sample_rate)),
				bitrate_audio=to_int(bitrate),
				resolution=(0, 0)
			)
		else:
			transcode(
				input_file=input_file,
				output_file=output_file,
				overwrite=overwrite_mode,
				mute=mute_mode,
				loop=to_int(loop),
				debug=debug_mode,
				thread_count=to_int(threads_value),
				thread_type=str(thread_type),
				video_encoder=str(codec_input),
				pixel_fmt=str(sample_fmt),
			)

		return None


if __name__ == "__main__":
	SimpleMP().run()
