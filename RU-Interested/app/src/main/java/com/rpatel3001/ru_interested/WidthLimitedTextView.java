package com.rpatel3001.ru_interested;

import android.content.Context;
import android.content.res.TypedArray;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.Point;
import android.graphics.drawable.Drawable;
import android.text.TextPaint;
import android.util.AttributeSet;
import android.view.View;
import android.view.WindowManager;
import android.widget.TextView;

public class WidthLimitedTextView extends TextView {
    public WidthLimitedTextView(Context context) {
        super(context);
    }

    public WidthLimitedTextView(Context context, AttributeSet attrs) {
        super(context, attrs);
    }

    public WidthLimitedTextView(Context context, AttributeSet attrs, int defStyle) {
        super(context, attrs, defStyle);
    }

    @Override
    protected void onMeasure(int widthMeasureSpec, int heightMeasureSpec) {
        Point size = new Point();
        // Adjust width as necessary
        ((WindowManager) getContext().getSystemService(Context.WINDOW_SERVICE)).getDefaultDisplay().getSize(size);
        int maxwidth = (int)(size.x * .40);
        int measuredWidth = MeasureSpec.getSize(widthMeasureSpec);
        if(maxwidth < measuredWidth) {
            int measureMode = MeasureSpec.getMode(widthMeasureSpec);
            widthMeasureSpec = MeasureSpec.makeMeasureSpec(maxwidth, measureMode);
        }
        super.onMeasure(widthMeasureSpec, heightMeasureSpec);
    }
}
