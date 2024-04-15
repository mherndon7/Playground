from plotly.graph_objs.layout import Annotation

render_plots = True
generate = False
info_annotations = True


class Classification:
    def __init__(
        self,
        title: str,
        showTopLeft: bool,
        showTopRight: bool,
        showBottomLeft: bool,
        showBottomRight: bool,
    ) -> None:
        self.classification = title
        self.top_left = showTopLeft
        self.top_right = showTopRight
        self.bottom_left = showBottomLeft
        self.bottom_right = showBottomRight

    def get_classifications(
        self, is_3d: bool = False, show_sidebar: bool = False
    ) -> list[Annotation]:
        return [
            self.__create_classification(
                "left", "top", self.top_left, is_3d, show_sidebar
            ),
            self.__create_classification(
                "left", "bottom", self.bottom_left, is_3d, show_sidebar
            ),
            self.__create_classification(
                "right", "top", self.top_right, is_3d, show_sidebar
            ),
            self.__create_classification(
                "right", "bottom", self.bottom_right, is_3d, show_sidebar
            ),
        ]

    def __create_classification(
        self,
        xanchor: str,
        yanchor: str,
        show: bool = False,
        is_3d: bool = False,
        show_sidebar: bool = False,
    ) -> Annotation:
        shifts = self.__resolution_shifts(is_3d, show_sidebar)
        x = 1 if xanchor == "right" else 0
        y = 1 if yanchor == "top" else 0
        return Annotation(
            xref="paper",
            yref="paper",
            x=x,
            xshift=shifts[xanchor],
            xanchor=xanchor,
            y=y,
            yshift=shifts[yanchor],
            yanchor=yanchor,
            text=f"<b>{self.classification}</b>",
            showarrow=False,
            visible=show,
            font={"size": 10},
        )

    def __resolution_shifts(self, is_3d: bool = False, show_sidebar: bool = False):
        return {
            "top": 40,
            "bottom": -70 if info_annotations else -50,
            "left": -20 if is_3d else -30,
            "right": 65 if show_sidebar else 0,
        }


def get_miss_distance(distance: float) -> Annotation:
    return Annotation(
        x=-0.01,
        y=-0.13,
        xref="paper",
        yref="paper",
        text=f"Miss distance {distance:.2f} m",
        showarrow=False,
    )


def get_missile_info(text: str) -> Annotation:
    return Annotation(
        x=1.01,
        y=-0.13,
        xref="paper",
        yref="paper",
        text=f"Missile Info: {text}",
        showarrow=False,
    )
