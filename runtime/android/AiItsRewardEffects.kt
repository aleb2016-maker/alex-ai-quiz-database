package com.alex.quizengine

import androidx.compose.animation.core.CubicBezierEasing
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.drawscope.rotate
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlin.math.roundToInt
import kotlin.random.Random

@Composable
fun AiItsFinalRewardCard(
    score: Int,
    total: Int,
    attemptKey: Any,
    modifier: Modifier = Modifier
) {
    val reward = remember(score, total, attemptKey) {
        FinalRewardEngine.createReward(score = score, total = total)
    }

    Box(
        modifier = modifier
            .widthIn(max = 720.dp)
            .clip(RoundedCornerShape(28.dp))
            .border(
                width = 1.dp,
                color = Color(0x668BE9FD),
                shape = RoundedCornerShape(28.dp)
            )
            .background(
                Brush.linearGradient(
                    colors = listOf(
                        Color(0xFF101827),
                        Color(0xFF151B34),
                        Color(0xFF231A3D)
                    )
                )
            )
            .padding(22.dp)
    ) {
        Row(
            horizontalArrangement = Arrangement.spacedBy(18.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier
                    .size(68.dp)
                    .clip(RoundedCornerShape(22.dp))
                    .background(Color.White.copy(alpha = 0.12f)),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = reward.emoji,
                    fontSize = 36.sp
                )
            }

            Column(
                verticalArrangement = Arrangement.spacedBy(6.dp)
            ) {
                Text(
                    text = "Premio finale AI ITS",
                    color = Color(0xFF8BE9FD),
                    fontSize = 12.sp,
                    fontWeight = FontWeight.ExtraBold
                )

                Text(
                    text = reward.title,
                    color = Color.White,
                    fontSize = 25.sp,
                    fontWeight = FontWeight.ExtraBold
                )

                Text(
                    text = "${reward.score}/${reward.total} · ${reward.percent}% · ${reward.badge}",
                    color = Color(0xFFF1FA8C),
                    fontSize = 15.sp,
                    fontWeight = FontWeight.Bold
                )

                Text(
                    text = reward.message,
                    color = Color.White.copy(alpha = 0.88f),
                    fontSize = 15.sp,
                    lineHeight = 21.sp
                )
            }
        }
    }
}

@Composable
fun AiItsConfettiOverlay(
    visible: Boolean,
    animationKey: Any,
    modifier: Modifier = Modifier,
    particleCount: Int = 46
) {
    val particles = remember(animationKey) {
        List(particleCount.coerceIn(12, 120)) { index ->
            ConfettiParticle(
                startXFactor = Random.nextFloat() * 0.56f - 0.28f,
                endXFactor = Random.nextFloat() * 1.35f - 0.675f,
                riseFactor = 0.72f + Random.nextFloat() * 0.58f,
                size = 7f + Random.nextFloat() * 10f,
                rotation = if (Random.nextBoolean()) 360f + Random.nextFloat() * 540f else -360f - Random.nextFloat() * 540f,
                delayFactor = Random.nextFloat() * 0.16f,
                color = confettiColors[index % confettiColors.size]
            )
        }
    }

    val progress by animateFloatAsState(
        targetValue = if (visible) 1f else 0f,
        animationSpec = tween(
            durationMillis = 1850,
            easing = CubicBezierEasing(0.16f, 0.78f, 0.24f, 1f)
        ),
        label = "aiItsConfettiProgress"
    )

    if (progress <= 0f) return

    Canvas(modifier = modifier.fillMaxSize()) {
        val centerX = size.width / 2f
        val baseY = size.height + 42f

        particles.forEach { particle ->
            val localProgress = ((progress - particle.delayFactor) / (1f - particle.delayFactor))
                .coerceIn(0f, 1f)

            if (localProgress <= 0f) return@forEach

            val x = centerX +
                (particle.startXFactor * size.width) +
                (particle.endXFactor * size.width * localProgress)

            val y = baseY - (particle.riseFactor * size.height * localProgress)

            val alpha = when {
                localProgress < 0.08f -> localProgress / 0.08f
                localProgress > 0.78f -> (1f - localProgress) / 0.22f
                else -> 1f
            }.coerceIn(0f, 1f)

            rotate(
                degrees = particle.rotation * localProgress,
                pivot = Offset(x, y)
            ) {
                drawRoundRect(
                    color = particle.color.copy(alpha = alpha),
                    topLeft = Offset(x, y),
                    size = androidx.compose.ui.geometry.Size(
                        width = particle.size * 1.35f,
                        height = particle.size
                    ),
                    cornerRadius = androidx.compose.ui.geometry.CornerRadius(4f, 4f)
                )
            }
        }
    }
}

private data class ConfettiParticle(
    val startXFactor: Float,
    val endXFactor: Float,
    val riseFactor: Float,
    val size: Float,
    val rotation: Float,
    val delayFactor: Float,
    val color: Color
)

private val confettiColors = listOf(
    Color(0xFF8BE9FD),
    Color(0xFF50FA7B),
    Color(0xFFFFB86C),
    Color(0xFFFF79C6),
    Color(0xFFBD93F9),
    Color(0xFFF1FA8C),
    Color(0xFFFFFFFF)
)
