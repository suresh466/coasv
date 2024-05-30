/** @type {import('tailwindcss').Config} */
module.exports = {
	content: [
		"../common/templates/**/*.{html,js}",
		"../*/templates/**/*.{html,js}",
	],
	theme: {
		extend: {},
	},
	plugins: [],
};

/* Start a watcher
./tailwindcss -i input.css -o output.css --watch

Compile and minify your CSS for production
./tailwindcss -i input.css -o output.css --minify; */
