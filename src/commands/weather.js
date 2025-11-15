const { SlashCommandBuilder, EmbedBuilder } = require('discord.js');
const axios = require('axios');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('weather')
        .setDescription('Belirtilen şehir için hava durumu tahminini gösterir.')
        .addStringOption(option =>
            option.setName('city')
                .setDescription('Şehir adı')
                .setRequired(true))
        .addIntegerOption(option =>
            option.setName('days')
                .setDescription('Gün sayısı (1-5 arası)')
                .setRequired(true)
                .setMinValue(1)
                .setMaxValue(5)),
    async execute(interaction) {
        await interaction.deferReply();

        const city = interaction.options.getString('city');
        const days = interaction.options.getInteger('days');
        const apiKey = process.env.WEATHER_API_KEY;

        if (!apiKey) {
            return await interaction.followUp({ content: '❌ Hava durumu API anahtarı yapılandırılmamış.', ephemeral: true });
        }

        try {
            const response = await axios.get('https://api.tomorrow.io/v4/weather/forecast', {
                params: {
                    location: city,
                    apikey: apiKey,
                    timesteps: '1d',
                    units: 'metric'
                },
                timeout: 10000
            });

            const forecasts = response.data?.timelines?.daily || [];

            if (forecasts.length === 0) {
                return await interaction.followUp({ content: '❌ Geçerli bir hava durumu verisi bulunamadı.', ephemeral: true });
            }

            const embed = new EmbedBuilder()
                .setColor('#0099ff')
                .setTitle(`🌤️ ${city} için ${days} günlük hava tahmini`)
                .setTimestamp();

            for (let i = 0; i < Math.min(days, forecasts.length); i++) {
                const forecast = forecasts[i].values;
                const date = forecasts[i].time.split('T')[0];
                const temp = forecast.temperatureAvg;
                const humidity = forecast.humidityAvg;
                const windSpeed = forecast.windSpeedAvg;
                const precipitation = forecast.precipitationProbabilityAvg;

                embed.addFields({
                    name: `📅 ${date}`,
                    value: `🌡️ **Sıcaklık:** ${temp}°C\n💧 **Nem:** ${humidity}%\n💨 **Rüzgar:** ${windSpeed} km/h\n☔ **Yağış İhtimali:** ${precipitation}%`,
                    inline: false
                });
            }

            await interaction.followUp({ embeds: [embed] });
        } catch (error) {
            console.error('Weather error:', error);
            await interaction.followUp({ content: '❌ Hava durumu bilgisi alınamadı, lütfen şehri kontrol edin.', ephemeral: true });
        }
    }
};
