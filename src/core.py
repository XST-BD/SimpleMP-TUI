import os

from textual.app import App, on
from textual.containers import Horizontal, Container
from textual.widgets import Label, Input, Switch, RadioSet, RadioButton, Button

from simplemp.simplemp import transcode
from simplemp.validator import codec_dict, audio_sample_fmt_dict, pixel_fmt_dict, samplerate_range_dict, bitrate_range_dict, codec_cppt_support_list, codec_cpp_support_list

from src.ui.ui import MainUI
from src.utils.intInputValidator import int_input_validator
from src.utils.stringToInt import to_int
from src.utils.mediaType import media_type


class SimpleMP(App):
	CSS_PATH = "styles/styles.tcss"
	MAX_THREADS = os.cpu_count()

	@staticmethod
	def compose():
		yield MainUI()

	def __init__(self):
		super().__init__()
		self.media = None

	@on(Input.Changed)
	def on_input_changed(self, event: Input.Changed):
		if event.input.id == "output_file":
			filename = event.input.value.strip()
			ext = os.path.splitext(filename)[1].lower()

			self.update_codec_set(ext)

			self.media = media_type(ext)

			if self.media == "audio":
				self.query_one("#audio_container", Container).styles.display = "block"

				for widget in self.query(".video_container"):
					widget.styles.display = "none"
				self.query_one("#res_width", Input).value = ""
				self.query_one("#res_height", Input).value = ""
				self.query_one("#frame_rate", Input).value = "30"

			elif self.media == "video":
				self.query_one("#audio_container", Container).styles.display = "none"
				self.query_one("#codec_input", RadioSet).value = None
				self.query_one("#sample_fmt", RadioSet).value = None
				self.query_one("#bitrate", Input).value = ""
				self.query_one("#sample_rate", RadioSet).value = None

				for widget in self.query(".video_container"):
					widget.styles.display = "block"

			else:
				self.query_one("#audio_container", Container).styles.display = "none"
				self.query_one("#codec_input", RadioSet).value = None
				self.query_one("#sample_fmt", RadioSet).value = None
				self.query_one("#bitrate", Input).value = ""
				self.query_one("#sample_rate", RadioSet).value = None

				for widget in self.query(".video_container"):
					widget.styles.display = "none"
				self.query_one("#res_width", Input).value = ""
				self.query_one("#res_height", Input).value = ""
				self.query_one("#frame_rate", Input).value = "30"

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

		elif event.input.id == "frame_rate":
			event.input.value = int_input_validator(event.input.value, 120, 24)

		elif event.input.id == "res_width":
			event.input.value = int_input_validator(event.input.value, 1920, 800)

		elif event.input.id == "res_height":
			event.input.value = int_input_validator(event.input.value, 1080, 600)

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
		bitrate = self.query_one("#bitrate", Input)

		codec_input.value = None
		codec_input.remove_children()

		sample_fmt.value = None
		sample_fmt.remove_children()

		sample_rate.value = None
		sample_rate.remove_children()

		bitrate.disabled = True
		bitrate.placeholder = "Select a Codec first"
		bitrate.value = ""

		self.query_one("#cppt_container", Container).styles.display = "none"
		self.query_one("#cpp_container", Container).styles.display = "none"

		if ext in codec_dict:
			codecs = codec_dict[ext]
			if not codecs:
				codec_input.mount(Label("No codecs available", shrink=True))
				sample_fmt.mount(Label("Select a Codec first", shrink=True))
				sample_rate.mount(Label("Select a Codec first", shrink=True))
				bitrate.disabled = True
				bitrate.placeholder = "Select a Codec first"
				bitrate.value = ""
				self.query_one("#cppt_container", Container).styles.display = "none"
				self.query_one("#cpp_container", Container).styles.display = "none"
				return
		else:
			codec_input.mount(Label("No codecs available", shrink=True))
			sample_fmt.mount(Label("Select a Codec first", shrink=True))
			sample_rate.mount(Label("Select a Codec first", shrink=True))
			bitrate.disabled = True
			bitrate.placeholder = "Select a Codec first"
			bitrate.value = ""
			self.query_one("#cppt_container", Container).styles.display = "none"
			self.query_one("#cpp_container", Container).styles.display = "none"
			return

		for codec in codecs:
			codec_input.mount(RadioButton(codec))

		sample_fmt.mount(Label("Select a Codec first", shrink=True))
		sample_rate.mount(Label("Select a Codec first", shrink=True))
		bitrate.disabled = True
		bitrate.placeholder = "Select a Codec first"
		bitrate.value = ""
		self.query_one("#cppt_container", Container).styles.display = "none"
		self.query_one("#cpp_container", Container).styles.display = "none"

	@on(RadioSet.Changed, "#codec_input")
	def codec_changed(self, event: RadioSet.Changed):
		selected_button = event.pressed
		selected_codec = selected_button.label
		self.update_fmt_set(str(selected_codec))
		self.update_sample_rate_set(str(selected_codec))
		self.update_bitrate_range(str(selected_codec))

		if selected_codec in codec_cppt_support_list:
			self.query_one("#cpp_container", Container).styles.display = "block"
			self.query_one("#cppt_container", Container).styles.display = "block"
		elif selected_codec in codec_cpp_support_list:
			self.query_one("#cpp_container", Container).styles.display = "block"
			self.query_one("#cppt_container", Container).styles.display = "none"
		else:
			self.query_one("#cppt_container", Container).styles.display = "none"
			self.query_one("#cpp_container", Container).styles.display = "none"

	def update_fmt_set(self, selected_codec: str):
		fmt_set = self.query_one("#sample_fmt", RadioSet)
		fmt_set.value = None
		fmt_set.remove_children()

		fmt_dict = None

		if self.media == "audio":
			fmt_dict = audio_sample_fmt_dict
		elif self.media == "video":
			fmt_dict = pixel_fmt_dict

		if selected_codec in fmt_dict:
			fmts = fmt_dict[selected_codec]
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
		bitrate = self.query_one("#bitrate", Input)
		bitrate.disabled = False
		bitrate.value = ""

		if selected_codec in bitrate_range_dict:
			min_bitrate, max_bitrate = bitrate_range_dict[selected_codec]
			bitrate.placeholder = f"Number only ({min_bitrate} - {max_bitrate})"

		else:
			bitrate.disabled = True
			bitrate.placeholder = "No bitrate available"
			bitrate.value = ""

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
		bitrate = self.query_one("#bitrate", Input).value
		sample_rate = self.query_one("#sample_rate", RadioSet).pressed_button.label if self.query_one("#sample_rate", RadioSet).pressed_button else None
		frame_rate = self.query_one("#frame_rate", Input).value
		res_width = self.query_one("#res_width", Input).value
		res_height = self.query_one("#res_height", Input).value
		crf = self.query_one("#crf", Input).value
		profile = self.query_one("#profile", RadioSet).pressed_button.label if self.query_one("#profile", RadioSet).pressed_button else None
		preset = self.query_one("#preset", RadioSet).pressed_button.label if self.query_one("#preset", RadioSet).pressed_button else None
		tune = self.query_one("#tune", RadioSet).pressed_button.label if self.query_one("#tune", RadioSet).pressed_button else None
		# if not input_file or not output_file:
		# 	return self.notify("Input and output file are required!", severity="error")
		# if not codec_input:
		# 	return self.notify("Select a codec!", severity="error")

		# self.notify(f'''Transcoding started...
		# file: {input_file}
		# out: {output_file}
		# overwrite: {overwrite_mode}
		# mute: {mute_mode}
		# loop: {loop}
		# debug: {debug_mode}
		# threads: {threads_value} ({thread_type})
		# codec: {codec_input}
		# format: {sample_fmt}
		# bitrate: {bitrate}
		# sample rate: {sample_rate}
		# frame rate: {frame_rate}
		# resolution: {res_width}x{res_height}
		# crf: {crf}
		# profile: {profile}
		# preset: {preset}
		# tune: {tune}
		# ''', severity="info")
		#
		# return

		if self.media == "audio":
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
				bitrate_audio=to_int(bitrate),
				samplerate=to_int(str(sample_rate)),
				resolution=(0, 0)
			)
		elif self.media == "video":
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
				bitrate_video=to_int(bitrate),
				frame_rate=to_int(frame_rate),
				resolution=(to_int(res_width), to_int(res_height)),
				crf=to_int(crf),
				profile=str(profile),
				preset=str(preset),
				tune=str(tune)
			)
		else:
			self.notify("Extension not supported!", severity="error")

		return None


if __name__ == "__main__":
	SimpleMP().run()
