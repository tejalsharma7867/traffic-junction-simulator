from ui.app import App


def main():
    """
    Launch the Adaptive Traffic Junction Simulator.
    """
    app = App(
        intensity_name="MEDIUM",
        mode="adaptive",
        seed=42
    )

    app.run()


if __name__ == "__main__":
    main()